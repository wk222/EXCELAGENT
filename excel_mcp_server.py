# -*- coding: utf-8 -*-
"""
Excel智能体 MCP 服务器

基于Model Context Protocol构建的Excel数据分析服务器，
提供模块化的Excel文件分析、可视化和智能问答功能。
"""

import os
import json
import pandas as pd
import numpy as np  # 添加numpy导入
import traceback
import re
import datetime
import requests
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots  # 添加make_subplots导入
from typing import Dict, Any, List, Optional
import logging

# MCP imports
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 创建MCP服务器
mcp = FastMCP("Excel智能体")

# --- 常量配置 ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-XSkgjH9KkPYzp89YD7863e13F497415eB24cD3Af42CdA98a")
BASE_URL = os.getenv("OPENAI_BASE_URL", 'http://48.210.12.198:3000/v1')
MODEL_NAME = os.getenv("MODEL_NAME", "grok-3-mini")

PLOTLY_DEFAULT_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["sendDataToCloud", "zoom2d", "lasso2d", "zoomIn2d", "zoomOut2d","select2d"],
    "modeBarButtonsToAdd": ["resetScale2d", "hoverClosestCartesian", "toggleSpikelines"],
    "toImageButtonOptions": {
        "format": "png",
        "width": 1200,
        "height": 800,
        "scale": 1
    },
    "responsive": True,
    "scrollZoom": True
}

# --- Pydantic 模型定义 ---
class ExcelFileData(BaseModel):
    """Excel文件数据结构"""
    filename: str
    dataframe: List[Dict[str, Any]]
    columns: List[str]
    shape: tuple
    dtypes: Dict[str, str]
    current_sheet: Optional[str] = None
    sheet_names: Optional[List[str]] = None

class AnalysisResult(BaseModel):
    """分析结果结构"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class VisualizationResult(BaseModel):
    """可视化结果结构"""
    status: str
    charts: List[str] = []  # JSON格式的图表
    message: str = ""
    error: Optional[str] = None

# --- 核心模块 ---

class OpenAIClient:
    """OpenAI API客户端"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.base_url = BASE_URL
        self.model = MODEL_NAME
        
    def call_llm(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """调用LLM生成响应"""
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
                # 增加重试机制的超时设置
                timeout = 30 if retry_count == 0 else 60
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_msg = f"API调用失败: HTTP {response.status_code}"
                    if response.text:
                        error_msg += f", 响应: {response.text[:200]}"
                    logging.error(f"OpenAI API错误: {error_msg}")
                    
                    # 如果是客户端错误（4xx），不重试
                    if 400 <= response.status_code < 500:
                        raise Exception(error_msg)
                    
                    # 服务器错误（5xx）可以重试
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(error_msg)
                    
                    logging.warning(f"重试第 {retry_count} 次...")
                    continue
                    
            except requests.exceptions.Timeout as e:
                retry_count += 1
                timeout_msg = f"请求超时 (timeout={timeout}s)"
                logging.error(f"LLM调用超时: {timeout_msg}")
                
                if retry_count >= max_retries:
                    raise Exception(f"{timeout_msg}，重试 {max_retries} 次后仍然失败")
                
                logging.warning(f"重试第 {retry_count} 次...")
                continue
                
            except requests.exceptions.ConnectionError as e:
                error_msg = f"网络连接错误: {str(e)}"
                logging.error(error_msg)
                raise Exception(error_msg)
                
            except Exception as e:
                error_msg = f"LLM调用异常: {str(e)}"
                logging.error(error_msg)
                raise Exception(error_msg)
        
        # 这里应该不会到达，但为了安全起见
        raise Exception(f"重试 {max_retries} 次后仍然失败")

# 全局OpenAI客户端
llm_client = OpenAIClient()

class DataAnalyzer:
    """数据分析模块"""
    
    @staticmethod
    def get_dataframe_summary(df: pd.DataFrame, df_name: str = "df") -> str:
        """获取DataFrame基本摘要"""
        if df is None or not isinstance(df, pd.DataFrame):
            return f"DataFrame '{df_name}' 无效或为空。"
        
        if df.empty:
            return f"DataFrame '{df_name}' 为空 (0 行)。"

        summary_lines = []
        summary_lines.append(f"=== DataFrame '{df_name}' 数据摘要 ===")
        summary_lines.append(f"形状: {df.shape[0]} 行 × {df.shape[1]} 列")
        summary_lines.append(f"列名: {', '.join(df.columns.tolist())}")
        
        # 数据类型统计
        dtypes_count = df.dtypes.value_counts()
        summary_lines.append(f"数据类型分布: {dict(dtypes_count)}")
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary_lines.append(f"数值列 ({len(numeric_cols)}个): {', '.join(numeric_cols)}")
            desc = df[numeric_cols].describe()
            summary_lines.append("数值列统计:")
            summary_lines.append(desc.to_string())
        else:
            summary_lines.append("无数值列")
        
        # 文本列统计
        text_cols = df.select_dtypes(include=['object']).columns
        if len(text_cols) > 0:
            summary_lines.append(f"文本列 ({len(text_cols)}个): {', '.join(text_cols)}")
            for col in text_cols[:3]:  # 只显示前3个文本列的信息
                unique_count = df[col].nunique()
                summary_lines.append(f"  {col}: {unique_count} 个唯一值")
        
        # 数据预览
        summary_lines.append("前5行数据:")
        summary_lines.append(df.head().to_string())
        
        return "\n".join(summary_lines)

class CodeGenerator:
    """代码生成模块"""
    
    @staticmethod
    def generate_analysis_code(question: str, data_summary: str, df_name: str = "df") -> str:
        """生成数据分析代码"""
        prompt = f"""你是一个Python数据分析专家。请根据以下信息生成Python代码来分析Excel数据并回答用户问题。

用户问题: {question}

数据摘要:
{data_summary}

数据变量名: {df_name}

请生成Python代码来：
1. 分析数据以回答用户的问题
2. 如果需要，创建可视化图表（使用plotly）
3. 提供清晰的分析结果

重要要求：
- 使用提供的DataFrame变量名：{df_name}
- DataFrame已经正确加载，不要假设第一行是列名，直接使用现有的列名
- 使用 {df_name}.columns 来获取列名，使用 {df_name}.columns.tolist() 查看所有列
- 如果创建plotly图表，请将图表JSON添加到plotly_figures_json列表中：plotly_figures_json.append(fig.to_json())
- 确保代码可以安全执行
- 使用print()输出分析结果
- 代码要完整可执行，包含必要的导入语句
- 添加错误处理，避免列名不存在的问题
- 生成至少1-2个可视化图表
- 提供完整的统计分析结果

代码结构建议：
1. 首先检查数据基本信息
2. 进行数据清理和类型转换（如果需要）
3. 执行统计分析
4. 生成可视化图表
5. 输出总结

请只返回Python代码，用XML标签包裹：

<python>
# 你的分析代码
</python>"""

        response = llm_client.call_llm(prompt, max_tokens=40000)  # 增加到4000以确保完整代码
        
        # 改进的代码提取逻辑 - 使用XML标签
        # 1. 首先尝试XML标签提取
        code_match = re.search(r"<python>\s*(.*?)\s*</python>", response, re.DOTALL | re.IGNORECASE)
        if code_match:
            extracted_code = code_match.group(1).strip()
            logging.info("✅ 使用XML标签提取代码成功")
            return extracted_code
        
        # 2. 备用：尝试标准的```python块提取
        code_match = re.search(r"```python\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
        if code_match:
            extracted_code = code_match.group(1).strip()
            logging.info("✅ 使用```python块提取代码成功")
            return extracted_code
        
        # 3. 备用：尝试任何```代码块
        code_match = re.search(r"```\s*(.*?)\s*```", response, re.DOTALL)
        if code_match:
            extracted_code = code_match.group(1).strip()
            # 移除可能的语言标识符
            if extracted_code.startswith('python\n'):
                extracted_code = extracted_code[7:]
            logging.info("✅ 使用通用```块提取代码成功")
            return extracted_code
        
        # 4. 查找包含pandas或plotly的代码段
        if any(keyword in response for keyword in ["import pandas", "plotly", "plt.show", "fig.show", "print("]):
            # 尝试清理响应，移除markdown标记
            cleaned_response = response.strip()
            # 移除开头的```python或```
            if cleaned_response.startswith('```python'):
                cleaned_response = cleaned_response[9:].strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:].strip()
            # 移除结尾的```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3].strip()
            
            logging.info("✅ 通过关键词识别和清理提取代码")
            return cleaned_response
        
        # 5. 最后尝试：直接返回响应，假设整个响应就是代码
        logging.warning("⚠️ 无法识别代码格式，尝试直接使用响应内容")
        return response.strip()
    
    @staticmethod
    def generate_visualization_code(df_columns: List[str], chart_type: str = "auto") -> str:
        """生成可视化代码"""
        try:
            prompt = f"""请为包含以下列的Excel数据生成plotly可视化代码：

列名: {', '.join(df_columns)}
图表类型: {chart_type}

要求：
1. 根据数据列的类型自动选择合适的图表类型（如果chart_type为auto）
2. 生成多个不同角度的图表（2-4个）
3. 每个图表都要添加到plotly_figures_json列表中
4. 设置合适的标题和标签
5. 使用DataFrame变量名：df

请只返回Python代码，用XML标签包裹：

<python>
# 可视化代码
</python>"""

            response = llm_client.call_llm(prompt, max_tokens=30000)  # 增加到3000以确保完整的可视化代码
            
            # 提取代码 - 使用XML标签
            code_match = re.search(r"<python>\s*(.*?)\s*</python>", response, re.DOTALL | re.IGNORECASE)
            if code_match:
                logging.info("✅ 使用XML标签提取可视化代码成功")
                return code_match.group(1).strip()
            
            # 备用：尝试```python块
            code_match = re.search(r"```python\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
            if code_match:
                logging.info("✅ 使用```python块提取可视化代码成功")
                return code_match.group(1).strip()
            else:
                logging.warning("⚠️ 可视化代码提取失败，直接返回响应")
                return response.strip()
                
        except Exception as e:
            logging.warning(f"LLM生成可视化代码失败: {e}，使用备用代码")
            # 使用备用的基础可视化代码
            return CodeGenerator._generate_fallback_visualization(df_columns, chart_type)
    
    @staticmethod
    def _generate_fallback_visualization(df_columns: List[str], chart_type: str = "auto") -> str:
        """生成备用的基础可视化代码"""
        numeric_cols = [col for col in df_columns if any(keyword in str(col).lower() 
                       for keyword in ['数量', '金额', '价格', '销售', '收入', '成本', '利润', '分数', '评分'])]
        
        if not numeric_cols:
            # 如果没有明显的数值列，尝试使用前几列
            numeric_cols = df_columns[:2] if len(df_columns) >= 2 else df_columns
        
        text_cols = [col for col in df_columns if col not in numeric_cols]
        
        fallback_code = f"""
import plotly.express as px
import plotly.graph_objects as go

print("生成基础数据可视化图表...")

# 数据基本信息
print(f"数据形状: {{df.shape}}")
print(f"列名: {{df.columns.tolist()}}")

try:
    # 图表1: 数据概览
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=list(range(len(df))),
        y=[1] * len(df),
        name="数据行计数",
        text=[f"第{{i+1}}行" for i in range(len(df))],
        textposition="inside"
    ))
    fig1.update_layout(
        title="数据行数概览",
        xaxis_title="行索引",
        yaxis_title="计数"
    )
    plotly_figures_json.append(fig1.to_json())
    print("✓ 已生成数据概览图")
    
    # 图表2: 如果有数值列，创建柱状图
    numeric_columns = {numeric_cols}
    if numeric_columns and len(numeric_columns) > 0:
        first_numeric = list(numeric_columns)[0]
        if first_numeric in df.columns:
            fig2 = px.bar(
                df.head(10),  # 只显示前10行避免过于拥挤
                x=df.columns[0],  # 使用第一列作为x轴
                y=first_numeric,
                title=f"{{first_numeric}} 柱状图（前10行）"
            )
            plotly_figures_json.append(fig2.to_json())
            print(f"✓ 已生成 {{first_numeric}} 柱状图")
    
    # 图表3: 数据分布图
    if len(df.columns) >= 2:
        fig3 = px.scatter(
            df.head(20),  # 前20行
            x=df.columns[0],
            y=df.columns[1] if len(df.columns) > 1 else df.columns[0],
            title="数据分布散点图（前20行）"
        )
        plotly_figures_json.append(fig3.to_json())
        print("✓ 已生成数据分布图")
    
    print(f"总共生成了 {{len(plotly_figures_json)}} 个图表")
    
except Exception as e:
    print(f"生成图表时出现错误: {{e}}")
    print("数据列信息:")
    for i, col in enumerate(df.columns):
        print(f"  {{i+1}}. {{col}} - {{df[col].dtype}}")
"""
        
        return fallback_code.strip()

class CodeExecutor:
    """代码执行模块"""
    
    @staticmethod
    def execute_code(code: str, df: pd.DataFrame, df_name: str = "df") -> Dict[str, Any]:
        """安全执行Python代码"""
        if not code or not isinstance(df, pd.DataFrame):
            return {"error": "无效的代码或数据", "stdout": "", "stderr": "", "plotly_figures": []}
        
        buffer_stdout = StringIO()
        buffer_stderr = StringIO()
        results = {
            "stdout": "",
            "stderr": "",
            "plotly_figures": [],
            "error": None
        }
        
        # 准备安全的执行环境
        exec_globals = {
            "pd": pd, 
            "plt": plt, 
            "px": px, 
            "go": go,
            "pio": pio,
            "json": json,
            "np": np,  # 添加numpy
            "plotly_figures_json": [],
            "PLOTLY_DEFAULT_CONFIG": PLOTLY_DEFAULT_CONFIG,
            "make_subplots": make_subplots,  # 添加make_subplots
            df_name: df,
            "__builtins__": {
                'print': print, 'range': range, 'len': len, 'str': str, 'int': int,
                'float': float, 'list': list, 'dict': dict, 'tuple': tuple, 'zip': zip,
                'isinstance': isinstance, 'max': max, 'min': min, 'sum': sum,
                'True': True, 'False': False, 'None': None,
                '__import__': __import__,
                'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
                'IndexError': IndexError, 'KeyError': KeyError, 'AttributeError': AttributeError,
                'FileNotFoundError': FileNotFoundError, 'json': json,
                'open': open, 'globals': globals,
                'locals': locals,
                'isinstance': isinstance,
                # 添加缺失的警告和异常类
                'UserWarning': UserWarning,
                'DeprecationWarning': DeprecationWarning,
                'FutureWarning': FutureWarning,
                'RuntimeWarning': RuntimeWarning,
                'PendingDeprecationWarning': PendingDeprecationWarning,
                'ImportWarning': ImportWarning,
                'ResourceWarning': ResourceWarning,
                'Warning': Warning,
                'RuntimeError': RuntimeError,
                'StopIteration': StopIteration,
                'GeneratorExit': GeneratorExit,
                'SystemExit': SystemExit,
                'KeyboardInterrupt': KeyboardInterrupt,
                # 添加更多常用的内置函数和类型
                'set': set,
                'enumerate': enumerate,
                'sorted': sorted,
                'any': any,
                'all': all,
                'round': round,
                'abs': abs,
                'ord': ord,
                'chr': chr,
                'bin': bin,
                'hex': hex,
                'oct': oct,
                'pow': pow,
                'divmod': divmod,
                'slice': slice,
                'reversed': reversed,
                'filter': filter,
                'map': map,
                'hash': hash,
                'id': id,
                'type': type,
                'callable': callable,
                'hasattr': hasattr,
                'getattr': getattr,
                'setattr': setattr,
                'delattr': delattr,
                'frozenset': frozenset,
                'bytes': bytes,
                'bytearray': bytearray,
                'memoryview': memoryview,
                'object': object,
                'super': super,
                'property': property,
                'staticmethod': staticmethod,
                'classmethod': classmethod,
                'format': format,
                'repr': repr,
                'ascii': ascii,
                'iter': iter,
                'next': next
            }
        }
        
        try:
            with redirect_stdout(buffer_stdout), redirect_stderr(buffer_stderr):
                exec(code, exec_globals)
            
            results["stdout"] = buffer_stdout.getvalue()
            results["stderr"] = buffer_stderr.getvalue()
            results["plotly_figures"] = exec_globals.get('plotly_figures_json', [])
            
            if results["stderr"]:
                results["error"] = f"执行警告: {results['stderr']}"
                
        except Exception as e:
            results["error"] = f"执行错误: {str(e)}\n{traceback.format_exc()}"
            results["stdout"] = buffer_stdout.getvalue()
            results["stderr"] = buffer_stderr.getvalue()
        
        return results

class SummaryGenerator:
    """摘要生成模块"""
    
    @staticmethod
    def generate_summary(question: str, code: str, execution_results: Dict[str, Any]) -> str:
        """生成分析摘要"""
        prompt = f"""请根据以下信息生成Excel数据分析的摘要报告：

原始问题: {question}

执行的代码:
```python
{code}
```

执行结果:
输出: {execution_results.get('stdout', 'N/A')}
错误: {execution_results.get('error', '无')}
生成图表数量: {len(execution_results.get('plotly_figures', []))}

请提供一个简洁明了的中文摘要，包括：
1. 对用户问题的直接回答
2. 关键数据发现
3. 如果有图表，说明图表展示的信息
4. 如果有错误，解释可能的原因和建议

摘要要专业、准确、易懂。"""

        return llm_client.call_llm(prompt, max_tokens=1000)
    
    @staticmethod
    def generate_deep_analysis_report(
        stage2_question: str, 
        stage3_question: str,
        stage2_code: str, 
        stage2_execution_results: Dict[str, Any],
        data_summary: str = ""
    ) -> str:
        """生成阶段三的深度分析报告（不生成代码，只分析已有结果）"""
        
        # 准备阶段二的结果信息
        stage2_output = stage2_execution_results.get('stdout', '')
        stage2_charts_count = len(stage2_execution_results.get('plotly_figures', []))
        stage2_error = stage2_execution_results.get('error', '')
        
        prompt = f"""你是一位资深的数据分析专家和商业顾问。请基于已完成的数据分析结果，生成一份深度分析报告。

【分析背景】
阶段二分析问题: {stage2_question}
阶段三深度分析问题: {stage3_question}

【已完成的数据分析】
执行的分析代码:
```python
{stage2_code}
```

代码执行结果:
{stage2_output}

生成图表数量: {stage2_charts_count}个
执行状态: {"成功" if not stage2_error else f"部分成功，有警告: {stage2_error}"}

【数据背景信息】
{data_summary}

【任务要求】
请基于以上已完成的分析结果，生成一份专业的深度分析报告，包括：

1. **对问题的直接回答**
   - 针对阶段三问题的具体回答
   - 基于数据结果的事实性结论

2. **关键数据洞察**  
   - 从统计结果中提取的重要发现
   - 数据背后的趋势和模式
   - 异常值或特殊现象的解释

3. **业务含义分析**
   - 数据结果对业务的实际意义
   - 潜在的机会和风险
   - 影响因素分析

4. **可行性建议**
   - 基于分析结果的具体建议
   - 后续行动方案
   - 需要进一步关注的领域

5. **图表说明**
   - 解释生成的图表展示了什么信息
   - 图表反映的主要趋势和要点

请用专业、客观的语言撰写报告，注重实用性和可操作性。报告要易于理解，适合决策者阅读。"""

        return llm_client.call_llm(prompt, max_tokens=3000)

# --- 核心函数（可直接调用） ---

def analyze_excel_data_core(
    file_data: Dict[str, Any],
    question: str
) -> AnalysisResult:
    """
    完整的Excel数据分析（包含代码生成、执行和摘要）
    
    Args:
        file_data: Excel文件数据
        question: 分析问题
    """
    try:
        # 验证数据
        if not file_data or 'dataframe' not in file_data:
            return AnalysisResult(status="失败", message="无效的Excel文件数据", error="缺少dataframe数据")
        
        # 重建DataFrame
        df = pd.DataFrame(file_data['dataframe'])
        if df.empty:
            return AnalysisResult(status="失败", message="数据为空", error="DataFrame为空")
        
        # 1. 数据分析
        data_summary = DataAnalyzer.get_dataframe_summary(df, "df")
        
        # 2. 代码生成
        analysis_code = CodeGenerator.generate_analysis_code(question, data_summary, "df")
        
        # 3. 代码执行
        execution_results = CodeExecutor.execute_code(analysis_code, df, "df")
        
        # 4. 摘要生成
        summary = SummaryGenerator.generate_summary(question, analysis_code, execution_results)
        
        # 构建结果
        result_data = {
            "question": question,
            "file_info": {
                "filename": file_data.get('filename', '未知'),
                "shape": file_data.get('shape', df.shape),
                "columns": file_data.get('columns', df.columns.tolist())
            },
            "data_summary": data_summary,
            "generated_code": analysis_code,
            "execution_results": execution_results,
            "summary": summary
        }
        
        status = "成功" if not execution_results.get("error") else "部分成功"
        message = f"分析完成，生成了{len(execution_results.get('plotly_figures', []))}个图表"
        
        return AnalysisResult(
            status=status,
            message=message,
            data=result_data,
            error=execution_results.get("error")
        )
        
    except Exception as e:
        logging.error(f"分析Excel数据时出错: {e}", exc_info=True)
        return AnalysisResult(
            status="失败",
            message="分析过程中出现错误",
            error=str(e)
        )

def generate_visualizations_only_core(
    file_data: Dict[str, Any],
    chart_type: str = "auto"
) -> VisualizationResult:
    """
    仅生成数据可视化（不进行文本分析）
    
    Args:
        file_data: Excel文件数据
        chart_type: 图表类型 (auto, bar, line, scatter, pie等)
    """
    try:
        # 验证数据
        if not file_data or 'dataframe' not in file_data:
            return VisualizationResult(status="失败", message="无效的Excel文件数据", error="缺少dataframe数据")
        
        # 重建DataFrame
        df = pd.DataFrame(file_data['dataframe'])
        if df.empty:
            return VisualizationResult(status="失败", message="数据为空", error="DataFrame为空")
        
        # 生成可视化代码
        viz_code = CodeGenerator.generate_visualization_code(df.columns.tolist(), chart_type)
        
        # 执行代码
        execution_results = CodeExecutor.execute_code(viz_code, df, "df")
        
        if execution_results.get("error"):
            return VisualizationResult(
                status="失败",
                message="可视化生成失败",
                error=execution_results["error"]
            )
        
        charts = execution_results.get('plotly_figures', [])
        return VisualizationResult(
            status="成功",
            charts=charts,
            message=f"成功生成{len(charts)}个图表"
        )
        
    except Exception as e:
        logging.error(f"生成可视化时出错: {e}", exc_info=True)
        return VisualizationResult(
            status="失败",
            message="可视化生成过程中出现错误",
            error=str(e)
        )

def get_data_summary_core(file_data: Dict[str, Any]) -> AnalysisResult:
    """
    获取Excel数据摘要（不生成代码和图表）
    
    Args:
        file_data: Excel文件数据
    """
    try:
        if not file_data or 'dataframe' not in file_data:
            return AnalysisResult(status="失败", message="无效的Excel文件数据")
        
        df = pd.DataFrame(file_data['dataframe'])
        summary = DataAnalyzer.get_dataframe_summary(df, "df")
        
        return AnalysisResult(
            status="成功",
            message="数据摘要生成成功",
            data={"summary": summary}
        )
        
    except Exception as e:
        return AnalysisResult(
            status="失败",
            message="获取数据摘要失败",
            error=str(e)
        )

def execute_custom_code_core(
    file_data: Dict[str, Any],
    python_code: str
) -> AnalysisResult:
    """
    执行自定义Python代码
    
    Args:
        file_data: Excel文件数据
        python_code: 要执行的Python代码
    """
    try:
        if not file_data or 'dataframe' not in file_data:
            return AnalysisResult(status="失败", message="无效的Excel文件数据")
        
        df = pd.DataFrame(file_data['dataframe'])
        execution_results = CodeExecutor.execute_code(python_code, df, "df")
        
        status = "成功" if not execution_results.get("error") else "失败"
        return AnalysisResult(
            status=status,
            message=f"代码执行{'成功' if status == '成功' else '失败'}",
            data=execution_results,
            error=execution_results.get("error")
        )
        
    except Exception as e:
        return AnalysisResult(
            status="失败",
            message="代码执行出现异常",
            error=str(e)
        )

def generate_deep_analysis_core(
    stage2_question: str,
    stage3_question: str, 
    stage2_result: AnalysisResult,
    data_summary: str = ""
) -> AnalysisResult:
    """
    生成阶段三的深度分析报告（不生成新代码，基于阶段二结果）
    
    Args:
        stage2_question: 阶段二的分析问题
        stage3_question: 阶段三的深度分析问题  
        stage2_result: 阶段二的完整分析结果
        data_summary: 数据摘要信息
    """
    try:
        # 验证阶段二结果
        if not stage2_result or not stage2_result.data:
            return AnalysisResult(
                status="失败", 
                message="阶段二结果无效，无法进行深度分析",
                error="缺少阶段二的分析数据"
            )
        
        # 提取阶段二的关键信息
        stage2_code = stage2_result.data.get('generated_code', '')
        stage2_execution_results = stage2_result.data.get('execution_results', {})
        
        # 生成深度分析报告
        deep_analysis_report = SummaryGenerator.generate_deep_analysis_report(
            stage2_question=stage2_question,
            stage3_question=stage3_question,
            stage2_code=stage2_code,
            stage2_execution_results=stage2_execution_results,
            data_summary=data_summary
        )
        
        # 构建结果
        result_data = {
            "stage2_question": stage2_question,
            "stage3_question": stage3_question,
            "deep_analysis_report": deep_analysis_report,
            "stage2_summary": stage2_result.data.get('summary', ''),
            "stage2_charts_count": len(stage2_execution_results.get('plotly_figures', [])),
            "stage2_status": stage2_result.status
        }
        
        return AnalysisResult(
            status="成功",
            message="深度分析报告生成完成",
            data=result_data
        )
        
    except Exception as e:
        logging.error(f"生成深度分析报告时出错: {e}", exc_info=True)
        return AnalysisResult(
            status="失败",
            message="深度分析报告生成失败", 
            error=str(e)
        )

# --- MCP Tools ---

@mcp.tool()
def analyze_excel_data(
    file_data: Dict[str, Any],
    question: str
) -> AnalysisResult:
    """
    完整的Excel数据分析（包含代码生成、执行和摘要）
    
    Args:
        file_data: Excel文件数据
        question: 分析问题
    """
    return analyze_excel_data_core(file_data, question)

@mcp.tool()
def generate_visualizations_only(
    file_data: Dict[str, Any],
    chart_type: str = "auto"
) -> VisualizationResult:
    """
    仅生成数据可视化（不进行文本分析）
    
    Args:
        file_data: Excel文件数据
        chart_type: 图表类型 (auto, bar, line, scatter, pie等)
    """
    return generate_visualizations_only_core(file_data, chart_type)

@mcp.tool()
def get_data_summary(file_data: Dict[str, Any]) -> AnalysisResult:
    """
    获取Excel数据摘要（不生成代码和图表）
    
    Args:
        file_data: Excel文件数据
    """
    return get_data_summary_core(file_data)

@mcp.tool()
def execute_custom_code(
    file_data: Dict[str, Any],
    python_code: str
) -> AnalysisResult:
    """
    执行自定义Python代码
    
    Args:
        file_data: Excel文件数据
        python_code: 要执行的Python代码
    """
    return execute_custom_code_core(file_data, python_code)

# --- MCP Resources ---

@mcp.resource("excel://config")
def get_excel_config() -> str:
    """获取Excel智能体配置"""
    config = {
        "name": "Excel智能体 - 模块化版本",
        "version": "2.0.0",
        "features": {
            "complete_analysis": "完整分析（问答+可视化+摘要）",
            "visualization_only": "仅生成可视化图表",
            "summary_only": "仅获取数据摘要",
            "custom_code": "执行自定义代码"
        },
        "supported_chart_types": ["auto", "bar", "line", "scatter", "pie", "box", "violin"],
        "model": MODEL_NAME,
        "plotly_config": PLOTLY_DEFAULT_CONFIG
    }
    return json.dumps(config, ensure_ascii=False, indent=2)

@mcp.resource("excel://examples")
def get_usage_examples() -> str:
    """获取使用示例"""
    examples = {
        "完整分析": {
            "tool": "analyze_excel_data",
            "params": {
                "file_data": "Excel文件数据",
                "question": "分析销售数据的趋势并找出最佳产品"
            }
        },
        "仅可视化": {
            "tool": "generate_visualizations_only",
            "params": {
                "file_data": "Excel文件数据",
                "chart_type": "bar"
            }
        },
        "数据摘要": {
            "tool": "get_data_summary",
            "params": {
                "file_data": "Excel文件数据"
            }
        }
    }
    return json.dumps(examples, ensure_ascii=False, indent=2)

# --- 运行服务器 ---

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Excel智能体 MCP 服务器 - 模块化版本")
    parser.add_argument("--transport", choices=["stdio", "http", "sse"], 
                       default="stdio", help="传输协议 (默认: stdio)")
    
    args = parser.parse_args()
    
    print("🚀 启动Excel智能体 MCP 服务器 (模块化版本)")
    print(f"📡 传输协议: {args.transport}")
    print("🔧 可用功能:")
    print("  📊 analyze_excel_data - 完整分析")
    print("  📈 generate_visualizations_only - 仅生成图表") 
    print("  📋 get_data_summary - 仅获取摘要")
    print("  💻 execute_custom_code - 执行自定义代码")
    
    if args.transport == "stdio":
        print("\n📍 STDIO模式: 等待客户端连接...")
        print("💡 配置示例:")
        print('  "excel-analyzer": {')
        print('    "command": "python",')
        print('    "args": ["excel_mcp_server.py"]')
        print('  }')
    
    mcp.run()

# --- 导出接口 ---
__all__ = [
    # MCP工具
    'analyze_excel_data',
    'generate_visualizations_only', 
    'get_data_summary',
    'execute_custom_code',
    # 核心函数（可直接调用）
    'analyze_excel_data_core',
    'generate_visualizations_only_core',
    'get_data_summary_core', 
    'execute_custom_code_core',
    'generate_deep_analysis_core',
    # 功能模块类
    'DataAnalyzer',
    'CodeGenerator', 
    'CodeExecutor',
    'SummaryGenerator',
    'OpenAIClient',
    # 数据模型
    'AnalysisResult',
    'VisualizationResult',
    'ExcelFileData',
    # MCP服务器实例
    'mcp'
] 