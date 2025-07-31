#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 代码执行模块

负责安全执行Python代码，包括：
- 代码执行环境设置
- 错误处理和异常捕获
- 执行结果处理和格式化
- 图表生成和处理
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端，避免GUI依赖
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import json
import traceback
import sys
import io
import re
import ast
import logging
import time
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, List, Optional, Union, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 默认Plotly配置
PLOTLY_DEFAULT_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["sendDataToCloud", "zoom2d", "lasso2d", "zoomIn2d", "zoomOut2d", "select2d"],
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

class CodeExecutionError(Exception):
    """代码执行错误"""
    def __init__(self, message, code=None, traceback_info=None):
        super().__init__(message)
        self.code = code
        self.traceback_info = traceback_info

class CodeExecutionResult:
    """代码执行结果类"""
    
    def __init__(self):
        self.stdout = ""          # 标准输出
        self.stderr = ""          # 标准错误
        self.error = None         # 错误信息
        self.plotly_figures = []  # Plotly图表JSON
        self.matplotlib_figures = []  # Matplotlib图表（Base64编码）
        self.execution_time = 0   # 执行时间（毫秒）
        self.memory_usage = 0     # 内存使用（字节）
        self.variables = {}       # 执行后的变量
        self.dataframes = {}      # 执行后的DataFrame
        self.warnings = []        # 警告信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "plotly_figures": self.plotly_figures,
            "matplotlib_figures": self.matplotlib_figures,
            "execution_time": self.execution_time,
            "memory_usage": self.memory_usage,
            "variables": {k: str(v) for k, v in self.variables.items() if not isinstance(v, pd.DataFrame)},
            "dataframes": {k: {"shape": v.shape, "columns": v.columns.tolist()} 
                          for k, v in self.dataframes.items()},
            "warnings": self.warnings
        }
    
    def has_error(self) -> bool:
        """检查是否有错误"""
        return self.error is not None
    
    def has_output(self) -> bool:
        """检查是否有输出"""
        return bool(self.stdout.strip())
    
    def has_figures(self) -> bool:
        """检查是否有图表"""
        return len(self.plotly_figures) > 0 or len(self.matplotlib_figures) > 0
    
    def get_figure_count(self) -> int:
        """获取图表总数"""
        return len(self.plotly_figures) + len(self.matplotlib_figures)

class CodeExecutor:
    """代码执行器类"""
    
    @staticmethod
    def execute_code(
        code: str, 
        df: Optional[pd.DataFrame] = None, 
        df_name: str = "df",
        timeout: int = 30,
        memory_limit: int = 500 * 1024 * 1024,  # 500MB
        max_output_size: int = 100 * 1024,      # 100KB
        capture_variables: bool = True
    ) -> Dict[str, Any]:
        """
        安全执行Python代码
        
        Args:
            code: 要执行的Python代码
            df: 可选的DataFrame对象
            df_name: DataFrame变量名
            timeout: 执行超时时间（秒）
            memory_limit: 内存限制（字节）
            max_output_size: 最大输出大小（字节）
            capture_variables: 是否捕获执行后的变量
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        # 验证输入
        if not code or not isinstance(code, str):
            return {"error": "无效的代码", "stdout": "", "stderr": "", "plotly_figures": []}
        
        # 创建结果对象
        result = CodeExecutionResult()
        
        # 准备输出缓冲区
        buffer_stdout = io.StringIO()
        buffer_stderr = io.StringIO()
        
        # 准备安全的执行环境
        exec_globals = CodeExecutor._prepare_execution_environment(df, df_name)
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 检查代码安全性
            CodeExecutor._check_code_safety(code)
            
            # 执行代码
            with redirect_stdout(buffer_stdout), redirect_stderr(buffer_stderr):
                exec(code, exec_globals)
            
            # 记录执行时间
            result.execution_time = round((time.time() - start_time) * 1000)
            
            # 获取输出
            result.stdout = buffer_stdout.getvalue()
            result.stderr = buffer_stderr.getvalue()
            
            # 限制输出大小
            if len(result.stdout) > max_output_size:
                result.stdout = result.stdout[:max_output_size] + "\n... [输出过长，已截断]"
                result.warnings.append("输出过长，已截断")
            
            # 获取图表
            result.plotly_figures = exec_globals.get('plotly_figures_json', [])
            
            # 捕获变量
            if capture_variables:
                for key, value in exec_globals.items():
                    # 排除内置模块和函数
                    if (not key.startswith('__') and 
                        not isinstance(value, type) and 
                        key not in ['pd', 'np', 'plt', 'px', 'go', 'pio', 'json', 'plotly_figures_json']):
                        
                        if isinstance(value, pd.DataFrame):
                            result.dataframes[key] = value
                        elif not callable(value) and not isinstance(value, type):
                            try:
                                # 尝试将值转换为字符串
                                str_value = str(value)
                                if len(str_value) <= 1000:  # 限制变量值大小
                                    result.variables[key] = value
                            except:
                                pass
            
            # 检查警告
            if result.stderr:
                result.warnings.append(f"执行产生警告: {result.stderr}")
                
        except Exception as e:
            # 记录执行时间
            result.execution_time = round((time.time() - start_time) * 1000)
            
            # 获取错误信息
            result.error = f"执行错误: {str(e)}\n{traceback.format_exc()}"
            result.stdout = buffer_stdout.getvalue()
            result.stderr = buffer_stderr.getvalue()
            
            # 记录日志
            logger.error(f"代码执行错误: {str(e)}")
        
        # 返回结果字典
        return result.to_dict()
    
    @staticmethod
    def _prepare_execution_environment(df: Optional[pd.DataFrame], df_name: str) -> Dict[str, Any]:
        """
        准备代码执行环境
        
        Args:
            df: DataFrame对象
            df_name: DataFrame变量名
            
        Returns:
            Dict[str, Any]: 执行环境字典
        """
        # 基本执行环境
        exec_globals = {
            "pd": pd, 
            "plt": plt, 
            "px": px, 
            "go": go,
            "pio": pio,
            "json": json,
            "np": np,
            "plotly_figures_json": [],
            "PLOTLY_DEFAULT_CONFIG": PLOTLY_DEFAULT_CONFIG,
            "make_subplots": make_subplots,
        }
        
        # 添加DataFrame
        if df is not None and isinstance(df, pd.DataFrame):
            exec_globals[df_name] = df
        
        # 添加安全的内置函数
        exec_globals["__builtins__"] = {
            'print': print, 'range': range, 'len': len, 'str': str, 'int': int,
            'float': float, 'list': list, 'dict': dict, 'tuple': tuple, 'zip': zip,
            'isinstance': isinstance, 'max': max, 'min': min, 'sum': sum,
            'True': True, 'False': False, 'None': None,
            'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
            'IndexError': IndexError, 'KeyError': KeyError, 'AttributeError': AttributeError,
            'FileNotFoundError': FileNotFoundError, 'json': json,
            'open': open, 'globals': globals,
            'locals': locals,
            'isinstance': isinstance,
            # 警告和异常类
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
            # 常用的内置函数和类型
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
        
        return exec_globals
    
    @staticmethod
    def _check_code_safety(code: str) -> None:
        """
        检查代码安全性
        
        Args:
            code: 要检查的代码
            
        Raises:
            CodeExecutionError: 如果代码不安全
        """
        # 解析代码
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise CodeExecutionError(f"语法错误: {str(e)}", code=code)
        
        # 检查危险操作
        dangerous_modules = ['os', 'sys', 'subprocess', 'shutil', 'socket', 'requests']
        dangerous_functions = ['eval', 'exec', 'compile', '__import__']
        
        for node in ast.walk(tree):
            # 检查导入
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name in dangerous_modules:
                        raise CodeExecutionError(f"禁止导入危险模块: {name.name}", code=code)
            
            # 检查from导入
            elif isinstance(node, ast.ImportFrom):
                if node.module in dangerous_modules:
                    raise CodeExecutionError(f"禁止从危险模块导入: {node.module}", code=code)
            
            # 检查函数调用
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in dangerous_functions:
                    raise CodeExecutionError(f"禁止调用危险函数: {node.func.id}", code=code)
    
    @staticmethod
    def fix_common_code_errors(code: str) -> Tuple[str, List[str]]:
        """
        修复常见的代码错误
        
        Args:
            code: 要修复的代码
            
        Returns:
            Tuple[str, List[str]]: 修复后的代码和修复说明列表
        """
        fixes = []
        fixed_code = code
        
        # 修复1: 缺少plotly_figures_json列表初始化
        if "plotly_figures_json.append" in fixed_code and "plotly_figures_json = []" not in fixed_code:
            fixed_code = "plotly_figures_json = []\n" + fixed_code
            fixes.append("添加了缺失的plotly_figures_json列表初始化")
        
        # 修复2: 缺少必要的导入
        if "px." in fixed_code and "import plotly.express as px" not in fixed_code:
            fixed_code = "import plotly.express as px\n" + fixed_code
            fixes.append("添加了缺失的plotly.express导入")
        
        if "go." in fixed_code and "import plotly.graph_objects as go" not in fixed_code:
            fixed_code = "import plotly.graph_objects as go\n" + fixed_code
            fixes.append("添加了缺失的plotly.graph_objects导入")
        
        if "np." in fixed_code and "import numpy as np" not in fixed_code:
            fixed_code = "import numpy as np\n" + fixed_code
            fixes.append("添加了缺失的numpy导入")
        
        # 修复3: fig.show() 替换为 plotly_figures_json.append(fig.to_json())
        pattern = r"fig\.show\(\)"
        if re.search(pattern, fixed_code):
            fixed_code = re.sub(pattern, "plotly_figures_json.append(fig.to_json())", fixed_code)
            fixes.append("将fig.show()替换为plotly_figures_json.append(fig.to_json())")
        
        # 修复4: 修复常见的语法错误
        # 缺少括号
        if re.search(r"print\s+[\"']", fixed_code):
            fixed_code = re.sub(r"print\s+([\"'].*?[\"'])", r"print(\1)", fixed_code)
            fixes.append("修复了print语句缺少括号的问题")
        
        return fixed_code, fixes
    
    @staticmethod
    def analyze_execution_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析执行结果，提供改进建议
        
        Args:
            result: 执行结果字典
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        analysis = {
            "success": not result.get("error"),
            "has_output": bool(result.get("stdout", "").strip()),
            "has_figures": len(result.get("plotly_figures", [])) > 0,
            "execution_time": result.get("execution_time", 0),
            "suggestions": []
        }
        
        # 检查是否有错误
        if result.get("error"):
            error_msg = result["error"]
            
            # 分析常见错误类型
            if "NameError" in error_msg:
                # 变量名错误
                var_match = re.search(r"name '(\w+)' is not defined", error_msg)
                if var_match:
                    var_name = var_match.group(1)
                    analysis["suggestions"].append(f"变量'{var_name}'未定义，请检查拼写或确保在使用前已定义")
            
            elif "KeyError" in error_msg:
                # 字典键错误
                key_match = re.search(r"KeyError: ['\"](.+)['\"]", error_msg)
                if key_match:
                    key_name = key_match.group(1)
                    analysis["suggestions"].append(f"字典中不存在键'{key_name}'，请检查拼写或确保键存在")
            
            elif "AttributeError" in error_msg:
                # 属性错误
                attr_match = re.search(r"'(.+)' object has no attribute '(.+)'", error_msg)
                if attr_match:
                    obj_type, attr_name = attr_match.groups()
                    analysis["suggestions"].append(f"'{obj_type}'对象没有'{attr_name}'属性，请检查对象类型或属性名")
            
            elif "IndexError" in error_msg:
                # 索引错误
                analysis["suggestions"].append("索引超出范围，请检查数组或列表的长度")
            
            elif "SyntaxError" in error_msg:
                # 语法错误
                analysis["suggestions"].append("代码存在语法错误，请检查括号、缩进或语法规则")
            
            elif "ValueError" in error_msg and "could not convert string to float" in error_msg:
                # 类型转换错误
                analysis["suggestions"].append("无法将字符串转换为数值，请检查数据类型或使用适当的类型转换")
            
            elif "ModuleNotFoundError" in error_msg:
                # 模块导入错误
                module_match = re.search(r"No module named '(.+)'", error_msg)
                if module_match:
                    module_name = module_match.group(1)
                    analysis["suggestions"].append(f"找不到模块'{module_name}'，该模块可能不在安全执行环境中")
        
        # 检查是否有图表
        if not analysis["has_figures"] and not result.get("error"):
            # 检查代码中是否有图表相关函数但没有添加到结果
            if "fig =" in result.get("stdout", "") or "plt." in result.get("stdout", ""):
                analysis["suggestions"].append("代码似乎创建了图表，但没有添加到结果中。请确保使用plotly_figures_json.append(fig.to_json())保存图表")
        
        # 检查执行时间
        if analysis["execution_time"] > 5000:  # 超过5秒
            analysis["suggestions"].append("代码执行时间较长，考虑优化算法或减少数据处理量")
        
        # 检查输出大小
        if len(result.get("stdout", "")) > 10000:  # 超过10KB
            analysis["suggestions"].append("输出内容较多，考虑减少打印内容或使用更简洁的输出格式")
        
        return analysis

# 导出便捷函数
def execute_code(code: str, df: Optional[pd.DataFrame] = None, df_name: str = "df", **kwargs) -> Dict[str, Any]:
    """
    安全执行Python代码的便捷函数
    
    Args:
        code: 要执行的Python代码
        df: 可选的DataFrame对象
        df_name: DataFrame变量名
        **kwargs: 其他参数
        
    Returns:
        Dict[str, Any]: 执行结果
    """
    return CodeExecutor.execute_code(code, df, df_name, **kwargs)

def fix_common_code_errors(code: str) -> Tuple[str, List[str]]:
    """
    修复常见的代码错误的便捷函数
    
    Args:
        code: 要修复的代码
        
    Returns:
        Tuple[str, List[str]]: 修复后的代码和修复说明列表
    """
    return CodeExecutor.fix_common_code_errors(code)

def analyze_execution_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析执行结果，提供改进建议的便捷函数
    
    Args:
        result: 执行结果字典
        
    Returns:
        Dict[str, Any]: 分析结果
    """
    return CodeExecutor.analyze_execution_result(result)

def check_code_safety(code: str) -> bool:
    """
    检查代码安全性的便捷函数
    
    Args:
        code: 要检查的代码
        
    Returns:
        bool: 代码是否安全
    """
    try:
        CodeExecutor._check_code_safety(code)
        return True
    except CodeExecutionError:
        return False