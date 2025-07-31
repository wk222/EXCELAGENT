#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - LLM服务模块

负责LLM API调用和参数管理，包括：
- LLM API客户端
- 参数管理和验证
- 重试和错误处理
- 响应处理和解析
- 模型管理
"""

import streamlit as st
import requests
import os
import json
import time
import logging
import re
import backoff
import threading
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
from state import get_llm_settings, get_llm_parameter, log_action, set_processing_state

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMError(Exception):
    """LLM API调用错误"""
    def __init__(self, message, status_code=None, response=None, request_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.request_data = request_data
        self.timestamp = datetime.now().isoformat()

class LLMTimeoutError(LLMError):
    """LLM API调用超时错误"""
    pass

class LLMConnectionError(LLMError):
    """LLM API连接错误"""
    pass

class LLMResponseError(LLMError):
    """LLM API响应解析错误"""
    pass

class LLMRateLimitError(LLMError):
    """LLM API速率限制错误"""
    pass

class LLMAuthenticationError(LLMError):
    """LLM API认证错误"""
    pass

class LLMResponse:
    """LLM响应对象，包含原始响应和处理后的内容"""
    
    def __init__(self, raw_response=None, content=None, model=None, usage=None, finish_reason=None):
        self.raw_response = raw_response  # 原始API响应
        self.content = content            # 处理后的内容
        self.model = model                # 使用的模型
        self.usage = usage                # 令牌使用情况
        self.finish_reason = finish_reason  # 完成原因
        self.timestamp = datetime.now().isoformat()  # 响应时间戳
        self.processing_time = None       # 处理时间（毫秒）
    
    def set_processing_time(self, start_time):
        """设置处理时间"""
        self.processing_time = round((time.time() - start_time) * 1000)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'content': self.content,
            'model': self.model,
            'usage': self.usage,
            'finish_reason': self.finish_reason,
            'timestamp': self.timestamp,
            'processing_time': self.processing_time
        }
    
    def __str__(self):
        """字符串表示"""
        return self.content if self.content else ""

class LLMService:
    """LLM服务类，提供LLM API调用和参数管理功能"""
    
    def __init__(self):
        """初始化LLM服务"""
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_count = 0
        self.error_count = 0
        self.success_count = 0
        self.rate_limit_delay = 0.1  # 默认请求间隔（秒）
        self.lock = threading.Lock()  # 用于线程安全
    
    def call_llm(self, prompt, temperature=None, max_tokens=None, model=None, **kwargs):
        """
        调用LLM API
        
        Args:
            prompt: 提示词
            temperature: 温度参数（可选）
            max_tokens: 最大令牌数（可选）
            model: 模型名称（可选）
            **kwargs: 其他LLM参数
            
        Returns:
            str: LLM响应内容
            
        Raises:
            LLMError: LLM API调用错误
            LLMTimeoutError: LLM API调用超时
            LLMConnectionError: LLM API连接错误
            LLMResponseError: LLM API响应解析错误
            LLMRateLimitError: LLM API速率限制错误
            LLMAuthenticationError: LLM API认证错误
        """
        # 获取LLM设置
        llm_settings = get_llm_settings()
        
        # 使用传入的参数或默认设置
        api_key = kwargs.get('api_key', llm_settings['api_key'])
        base_url = kwargs.get('base_url', llm_settings['base_url'])
        model = model or llm_settings['model']
        temperature = temperature if temperature is not None else llm_settings['temperature']
        max_tokens = max_tokens if max_tokens is not None else llm_settings['max_tokens']
        timeout = kwargs.get('timeout', llm_settings.get('timeout', 60))
        retries = kwargs.get('retries', llm_settings.get('retries', 2))
        
        # 获取高级参数
        top_p = kwargs.get('top_p', llm_settings.get('top_p', 1.0))
        frequency_penalty = kwargs.get('frequency_penalty', llm_settings.get('frequency_penalty', 0.0))
        presence_penalty = kwargs.get('presence_penalty', llm_settings.get('presence_penalty', 0.0))
        stop_sequences = kwargs.get('stop_sequences', llm_settings.get('stop_sequences', []))
        stream = kwargs.get('stream', False)
        
        # 验证参数
        self._validate_parameters(temperature, max_tokens, model)
        
        # 准备请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 准备消息
        messages = kwargs.get('messages', None)
        if messages is None:
            messages = [{"role": "user", "content": prompt}]
        
        # 准备请求数据
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stream": stream
        }
        
        # 只有当stop_sequences非空时才添加
        if stop_sequences:
            data["stop"] = stop_sequences
        
        # 记录请求开始
        log_action("llm_api_call", {
            "model": model, 
            "temperature": temperature, 
            "max_tokens": max_tokens,
            "prompt_length": len(prompt) if isinstance(prompt, str) else "multiple_messages"
        })
        set_processing_state(True)
        
        # 记录开始时间
        start_time = time.time()
        
        # 使用backoff装饰器处理重试
        response = self._call_api_with_retry(
            base_url=base_url,
            headers=headers,
            data=data,
            timeout=timeout,
            max_retries=retries
        )
        
        # 处理响应
        try:
            if stream:
                # 流式响应处理
                return self._process_streaming_response(response, start_time)
            else:
                # 普通响应处理
                return self._process_response(response, start_time)
        except Exception as e:
            error_msg = f"处理LLM响应时出错: {str(e)}"
            logger.error(error_msg)
            set_processing_state(False, error_msg)
            raise LLMResponseError(error_msg, request_data=data)
    
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, LLMRateLimitError),
        max_tries=3,  # 最大重试次数
        max_time=300,  # 最大重试时间（秒）
        on_backoff=lambda details: logger.warning(
            f"重试第 {details['tries']} 次，等待 {details['wait']:.1f} 秒..."
        )
    )
    def _call_api_with_retry(self, base_url, headers, data, timeout, max_retries):
        """
        使用重试机制调用API
        
        Args:
            base_url: API基础URL
            headers: 请求头
            data: 请求数据
            timeout: 超时时间
            max_retries: 最大重试次数
            
        Returns:
            requests.Response: API响应
            
        Raises:
            LLMError: 各种LLM API调用错误
        """
        # 限制请求频率
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
            
            self.last_request_time = time.time()
            self.request_count += 1
        
        try:
            response = self.session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            
            # 处理HTTP错误
            if response.status_code != 200:
                # 处理特定错误
                if response.status_code == 401:
                    error_msg = "API认证失败: 无效的API密钥"
                    logger.error(error_msg)
                    set_processing_state(False, error_msg)
                    raise LLMAuthenticationError(error_msg, status_code=response.status_code, response=response.text, request_data=data)
                
                elif response.status_code == 429:
                    error_msg = "API速率限制: 请求过于频繁"
                    logger.error(error_msg)
                    
                    # 增加延迟
                    with self.lock:
                        self.rate_limit_delay *= 2  # 指数退避
                    
                    # 如果响应中包含重试信息，使用它
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            retry_after = float(retry_after)
                            logger.info(f"按照API建议等待 {retry_after} 秒")
                            time.sleep(retry_after)
                        except:
                            pass
                    
                    raise LLMRateLimitError(error_msg, status_code=response.status_code, response=response.text, request_data=data)
                
                else:
                    error_msg = f"API调用失败: HTTP {response.status_code}"
                    if response.text:
                        try:
                            error_json = response.json()
                            if 'error' in error_json:
                                error_msg += f", 错误: {error_json['error'].get('message', '')}"
                        except:
                            error_msg += f", 响应: {response.text[:200]}"
                    
                    logger.error(f"LLM API错误: {error_msg}")
                    set_processing_state(False, error_msg)
                    
                    # 客户端错误（4xx）和服务器错误（5xx）区分处理
                    if 400 <= response.status_code < 500:
                        raise LLMError(error_msg, status_code=response.status_code, response=response.text, request_data=data)
                    else:
                        # 服务器错误可以重试
                        raise requests.exceptions.RequestException(error_msg)
            
            # 成功响应
            with self.lock:
                self.success_count += 1
                # 成功后逐渐减少延迟，但不低于初始值
                self.rate_limit_delay = max(0.1, self.rate_limit_delay * 0.9)
            
            return response
            
        except requests.exceptions.Timeout:
            error_msg = f"请求超时 (timeout={timeout}s)"
            logger.error(f"LLM调用超时: {error_msg}")
            set_processing_state(False, error_msg)
            
            with self.lock:
                self.error_count += 1
            
            raise LLMTimeoutError(error_msg, request_data=data)
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"网络连接错误: {str(e)}"
            logger.error(error_msg)
            set_processing_state(False, error_msg)
            
            with self.lock:
                self.error_count += 1
            
            raise LLMConnectionError(error_msg, request_data=data)
            
        except Exception as e:
            error_msg = f"LLM调用异常: {str(e)}"
            logger.error(error_msg)
            set_processing_state(False, error_msg)
            
            with self.lock:
                self.error_count += 1
            
            raise LLMError(error_msg, request_data=data)
    
    def _process_response(self, response, start_time):
        """
        处理API响应
        
        Args:
            response: API响应对象
            start_time: 请求开始时间
            
        Returns:
            str: 处理后的响应内容
            
        Raises:
            LLMResponseError: 响应处理错误
        """
        try:
            result = response.json()
            
            # 创建响应对象
            llm_response = LLMResponse(
                raw_response=result,
                content=result["choices"][0]["message"]["content"],
                model=result.get("model", "unknown"),
                usage=result.get("usage", {}),
                finish_reason=result["choices"][0].get("finish_reason", "unknown")
            )
            
            # 设置处理时间
            llm_response.set_processing_time(start_time)
            
            # 记录请求成功
            set_processing_state(False)
            
            # 记录令牌使用情况
            if "usage" in result:
                log_action("llm_token_usage", {
                    "prompt_tokens": result["usage"].get("prompt_tokens", 0),
                    "completion_tokens": result["usage"].get("completion_tokens", 0),
                    "total_tokens": result["usage"].get("total_tokens", 0)
                })
            
            return llm_response.content
            
        except KeyError as e:
            error_msg = f"响应格式错误: {str(e)}"
            logger.error(error_msg)
            set_processing_state(False, error_msg)
            raise LLMResponseError(error_msg, response=response.text)
            
        except json.JSONDecodeError as e:
            error_msg = f"响应解析错误: {str(e)}"
            logger.error(error_msg)
            set_processing_state(False, error_msg)
            raise LLMResponseError(error_msg, response=response.text)
    
    def _process_streaming_response(self, response, start_time):
        """
        处理流式API响应
        
        Args:
            response: API响应对象
            start_time: 请求开始时间
            
        Returns:
            str: 处理后的响应内容
            
        Raises:
            LLMResponseError: 响应处理错误
        """
        try:
            content = []
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # 去掉 'data: ' 前缀
                        if data.strip() == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content.append(delta['content'])
                                    # 这里可以添加回调函数来实时处理内容
                        except json.JSONDecodeError:
                            pass
            
            # 合并所有内容
            full_content = ''.join(content)
            
            # 创建响应对象
            llm_response = LLMResponse(
                content=full_content,
                model="streaming_model"
            )
            
            # 设置处理时间
            llm_response.set_processing_time(start_time)
            
            # 记录请求成功
            set_processing_state(False)
            
            return full_content
            
        except Exception as e:
            error_msg = f"处理流式响应错误: {str(e)}"
            logger.error(error_msg)
            set_processing_state(False, error_msg)
            raise LLMResponseError(error_msg)
    
    def _validate_parameters(self, temperature, max_tokens, model):
        """
        验证LLM参数
        
        Args:
            temperature: 温度参数
            max_tokens: 最大令牌数
            model: 模型名称
            
        Raises:
            ValueError: 参数验证错误
        """
        # 验证温度参数
        if temperature is not None:
            if not isinstance(temperature, (int, float)):
                raise ValueError(f"温度参数必须是数字，而不是 {type(temperature)}")
            if temperature < 0 or temperature > 2:
                raise ValueError(f"温度参数必须在0到2之间，而不是 {temperature}")
        
        # 验证最大令牌数
        if max_tokens is not None:
            if not isinstance(max_tokens, int):
                raise ValueError(f"最大令牌数必须是整数，而不是 {type(max_tokens)}")
            if max_tokens <= 0:
                raise ValueError(f"最大令牌数必须大于0，而不是 {max_tokens}")
        
        # 验证模型名称
        if model is not None:
            if not isinstance(model, str):
                raise ValueError(f"模型名称必须是字符串，而不是 {type(model)}")
            if not model.strip():
                raise ValueError("模型名称不能为空")
    
    def validate_api_settings(self, api_key=None, base_url=None):
        """
        验证API设置
        
        Args:
            api_key: API密钥（可选）
            base_url: API基础URL（可选）
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 获取LLM设置
        llm_settings = get_llm_settings()
        
        # 使用传入的参数或默认设置
        api_key = api_key or llm_settings['api_key']
        base_url = base_url or llm_settings['base_url']
        
        # 验证API密钥和基础URL
        if not api_key:
            return (False, "API密钥不能为空")
        
        if not base_url:
            return (False, "API基础URL不能为空")
        
        # 准备请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 发送简单请求验证API设置
        try:
            response = self.session.get(
                f"{base_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # 尝试解析响应
                try:
                    models_data = response.json()
                    if 'data' in models_data and isinstance(models_data['data'], list):
                        model_count = len(models_data['data'])
                        return (True, f"API设置有效，可用模型数量: {model_count}")
                    else:
                        return (True, "API设置有效，但模型列表格式不符合预期")
                except json.JSONDecodeError:
                    return (True, "API设置有效，但响应解析失败")
            else:
                error_msg = f"API验证失败: HTTP {response.status_code}"
                if response.text:
                    try:
                        error_json = response.json()
                        if 'error' in error_json:
                            error_msg += f", 错误: {error_json['error'].get('message', '')}"
                    except:
                        error_msg += f", 响应: {response.text[:200]}"
                return (False, error_msg)
                
        except requests.exceptions.Timeout:
            return (False, "API验证超时，请检查网络连接或API服务器状态")
            
        except requests.exceptions.ConnectionError as e:
            return (False, f"API连接错误: {str(e)}")
            
        except Exception as e:
            return (False, f"API验证异常: {str(e)}")
    
    def get_available_models(self):
        """
        获取可用的模型列表
        
        Returns:
            list: 可用模型列表
        """
        # 默认模型列表
        default_models = [
            "grok-3-mini",
            "gpt-3.5-turbo",
            "gpt-4",
            "claude-3-opus",
            "claude-3-sonnet"
        ]
        
        # 获取LLM设置
        llm_settings = get_llm_settings()
        api_key = llm_settings['api_key']
        base_url = llm_settings['base_url']
        
        # 如果没有API密钥，返回默认列表
        if not api_key:
            return default_models
        
        # 准备请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 尝试获取可用模型
        try:
            response = self.session.get(
                f"{base_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                models_data = response.json()
                if 'data' in models_data and isinstance(models_data['data'], list):
                    # 提取模型ID
                    models = [model['id'] for model in models_data['data'] if 'id' in model]
                    # 如果获取到的模型列表为空，返回默认列表
                    return models if models else default_models
            
            # 如果请求失败，返回默认列表
            logger.warning(f"获取模型列表失败: HTTP {response.status_code}")
            return default_models
                
        except Exception as e:
            logger.error(f"获取模型列表失败: {str(e)}")
            return default_models
    
    def extract_code_from_response(self, response_text):
        """
        从LLM响应中提取代码块
        
        Args:
            response_text: LLM响应文本
            
        Returns:
            list: 提取的代码块列表
        """
        # 匹配Markdown代码块: ```python ... ```
        code_blocks = re.findall(r'```(?:python)?\s*([\s\S]*?)```', response_text)
        
        # 如果没有找到代码块，尝试查找可能的代码片段
        if not code_blocks:
            # 尝试查找缩进的代码行
            lines = response_text.split('\n')
            code_lines = []
            in_code_block = False
            
            for line in lines:
                # 检查是否是代码行（缩进或常见Python语法）
                if line.strip().startswith('def ') or line.strip().startswith('class ') or line.strip().startswith('import '):
                    in_code_block = True
                    code_lines.append(line)
                elif in_code_block:
                    if line.strip() == '' and len(code_lines) > 0:
                        # 空行可能表示代码块结束
                        if len(code_lines) >= 3:  # 至少有3行才认为是代码块
                            code_blocks.append('\n'.join(code_lines))
                        code_lines = []
                        in_code_block = False
                    else:
                        code_lines.append(line)
            
            # 检查最后一个代码块
            if in_code_block and len(code_lines) >= 3:
                code_blocks.append('\n'.join(code_lines))
        
        return code_blocks
    
    def extract_json_from_response(self, response_text):
        """
        从LLM响应中提取JSON
        
        Args:
            response_text: LLM响应文本
            
        Returns:
            list: 提取的JSON对象列表
        """
        # 匹配JSON块: ```json ... ``` 或 { ... }
        json_blocks = []
        
        # 尝试匹配Markdown JSON块
        md_json_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)```', response_text)
        
        for block in md_json_blocks:
            try:
                # 确保块以 { 开始
                if block.strip().startswith('{'):
                    json_obj = json.loads(block)
                    json_blocks.append(json_obj)
            except json.JSONDecodeError:
                pass
        
        # 如果没有找到有效的JSON块，尝试直接匹配 { ... }
        if not json_blocks:
            # 查找可能的JSON对象
            brace_pattern = re.compile(r'({[\s\S]*?})')
            potential_jsons = brace_pattern.findall(response_text)
            
            for potential_json in potential_jsons:
                try:
                    json_obj = json.loads(potential_json)
                    json_blocks.append(json_obj)
                except json.JSONDecodeError:
                    pass
        
        return json_blocks
    
    def parse_structured_response(self, response_text, expected_format=None):
        """
        解析结构化响应
        
        Args:
            response_text: LLM响应文本
            expected_format: 期望的格式 ('json', 'code', 'list', 'table', None)
            
        Returns:
            dict: 解析结果
        """
        result = {
            'original': response_text,
            'format': 'text',
            'parsed': None,
            'success': False
        }
        
        # 如果没有指定格式，尝试自动检测
        if expected_format is None:
            # 检查是否包含代码块
            if '```' in response_text:
                expected_format = 'code'
            # 检查是否包含JSON
            elif '{' in response_text and '}' in response_text:
                expected_format = 'json'
            # 检查是否包含列表
            elif re.search(r'^\s*[-*]\s', response_text, re.MULTILINE):
                expected_format = 'list'
            # 检查是否包含表格
            elif '|' in response_text and '-|-' in response_text:
                expected_format = 'table'
        
        # 根据格式解析
        if expected_format == 'json':
            json_blocks = self.extract_json_from_response(response_text)
            if json_blocks:
                result['format'] = 'json'
                result['parsed'] = json_blocks[0] if len(json_blocks) == 1 else json_blocks
                result['success'] = True
        
        elif expected_format == 'code':
            code_blocks = self.extract_code_from_response(response_text)
            if code_blocks:
                result['format'] = 'code'
                result['parsed'] = code_blocks[0] if len(code_blocks) == 1 else code_blocks
                result['success'] = True
        
        elif expected_format == 'list':
            # 解析Markdown列表
            list_items = re.findall(r'^\s*[-*]\s+(.*?)$', response_text, re.MULTILINE)
            if list_items:
                result['format'] = 'list'
                result['parsed'] = list_items
                result['success'] = True
        
        elif expected_format == 'table':
            # 解析Markdown表格
            table_pattern = re.compile(r'\|(.+?)\|\s*\n\|[-|]+\|\s*\n((?:\|.+?\|\s*\n)+)', re.MULTILINE)
            table_match = table_pattern.search(response_text)
            
            if table_match:
                headers = [h.strip() for h in table_match.group(1).split('|') if h.strip()]
                rows_text = table_match.group(2)
                rows = []
                
                for row_text in rows_text.strip().split('\n'):
                    cells = [cell.strip() for cell in row_text.split('|')[1:-1]]
                    if len(cells) == len(headers):
                        rows.append(dict(zip(headers, cells)))
                
                if rows:
                    result['format'] = 'table'
                    result['parsed'] = {
                        'headers': headers,
                        'rows': rows
                    }
                    result['success'] = True
        
        return result
    
    def get_stats(self):
        """
        获取LLM服务统计信息
        
        Returns:
            dict: 统计信息
        """
        return {
            'request_count': self.request_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': (self.success_count / self.request_count * 100) if self.request_count > 0 else 0,
            'rate_limit_delay': self.rate_limit_delay
        }

# 创建LLM服务实例
llm_service = LLMService()

# 导出函数
def call_llm(prompt, temperature=None, max_tokens=None, model=None, **kwargs):
    """
    调用LLM API的便捷函数
    
    Args:
        prompt: 提示词
        temperature: 温度参数（可选）
        max_tokens: 最大令牌数（可选）
        model: 模型名称（可选）
        **kwargs: 其他LLM参数
        
    Returns:
        str: LLM响应内容
    """
    return llm_service.call_llm(prompt, temperature, max_tokens, model, **kwargs)

def validate_api_settings(api_key=None, base_url=None):
    """
    验证API设置的便捷函数
    
    Args:
        api_key: API密钥（可选）
        base_url: API基础URL（可选）
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    return llm_service.validate_api_settings(api_key, base_url)

def get_available_models():
    """
    获取可用模型列表的便捷函数
    
    Returns:
        list: 可用模型列表
    """
    return llm_service.get_available_models()

def extract_code_from_response(response_text):
    """
    从LLM响应中提取代码块的便捷函数
    
    Args:
        response_text: LLM响应文本
        
    Returns:
        list: 提取的代码块列表
    """
    return llm_service.extract_code_from_response(response_text)

def extract_json_from_response(response_text):
    """
    从LLM响应中提取JSON的便捷函数
    
    Args:
        response_text: LLM响应文本
        
    Returns:
        list: 提取的JSON对象列表
    """
    return llm_service.extract_json_from_response(response_text)

def parse_structured_response(response_text, expected_format=None):
    """
    解析结构化响应的便捷函数
    
    Args:
        response_text: LLM响应文本
        expected_format: 期望的格式 ('json', 'code', 'list', 'table', None)
        
    Returns:
        dict: 解析结果
    """
    return llm_service.parse_structured_response(response_text, expected_format)

def get_llm_settings_summary():
    """
    获取LLM设置摘要，用于显示
    
    Returns:
        dict: 包含格式化后的LLM设置信息
    """
    llm_settings = get_llm_settings()
    
    # 创建摘要
    summary = {
        'model': llm_settings['model'],
        'temperature': f"{llm_settings['temperature']:.1f}",
        'max_tokens': str(llm_settings['max_tokens']),
        'api_configured': bool(llm_settings['api_key']),
        'advanced_params_configured': any([
            llm_settings.get('top_p', 1.0) != 1.0,
            llm_settings.get('frequency_penalty', 0.0) != 0.0,
            llm_settings.get('presence_penalty', 0.0) != 0.0,
            llm_settings.get('stop_sequences', [])
        ]),
        'settings_persistent': llm_settings.get('remember_settings', True)
    }
    
    # 添加统计信息
    stats = llm_service.get_stats()
    if stats['request_count'] > 0:
        summary['stats'] = {
            'requests': stats['request_count'],
            'success_rate': f"{stats['success_rate']:.1f}%"
        }
    
    return summary

def get_llm_service_instance():
    """
    获取LLM服务实例
    
    Returns:
        LLMService: LLM服务实例
    """
    return llm_service