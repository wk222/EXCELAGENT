#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 数据处理模块

负责Excel文件的处理和数据准备，包括：
- Excel文件读取和解析
- 工作表管理
- 数据清理和验证
- 数据摘要和统计
- 数据过滤和转换
"""

import pandas as pd
import numpy as np
import io
import re
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Excel文件处理类，提供Excel文件的读取、处理和分析功能"""
    
    @staticmethod
    def process_excel_file(uploaded_file, sheet_name=None):
        """
        处理上传的Excel文件
        
        Args:
            uploaded_file: 上传的Excel文件对象
            sheet_name: 要处理的工作表名称，如果为None则读取第一个工作表
            
        Returns:
            dict: 包含处理后的数据和元数据
        """
        if uploaded_file is None:
            return None
        
        try:
            # 读取Excel文件
            excel_file = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
            sheet_names = excel_file.sheet_names
            
            # 如果未指定工作表，使用第一个
            if sheet_name is None or sheet_name not in sheet_names:
                sheet_name = sheet_names[0]
            
            # 读取指定工作表
            df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), sheet_name=sheet_name)
            
            # 数据清理：处理混合类型列和特殊字符
            cleaned_df = ExcelProcessor.clean_dataframe(df)
            
            # 数据验证
            validation_results = ExcelProcessor.validate_data(cleaned_df)
            
            # 准备文件数据
            file_data = {
                'filename': uploaded_file.name,
                'dataframe': df.to_dict('records'),  # 使用原始数据
                'columns': df.columns.tolist(),      # 使用原始列名
                'shape': df.shape,
                'dtypes': df.dtypes.astype(str).to_dict(),
                'current_sheet': sheet_name,
                'sheet_names': sheet_names,
                'cleaned_df': cleaned_df,  # 添加清理后的DataFrame
                'validation_results': validation_results  # 添加验证结果
            }
            
            return file_data
            
        except Exception as e:
            logger.error(f"处理Excel文件时出错: {str(e)}")
            raise Exception(f"处理Excel文件时出错: {str(e)}")

    @staticmethod
    def clean_dataframe(df):
        """
        清理DataFrame，处理混合类型和特殊字符
        
        Args:
            df: 原始DataFrame
            
        Returns:
            pd.DataFrame: 清理后的DataFrame
        """
        if df is None or df.empty:
            return df
        
        # 创建副本
        cleaned_df = df.copy()
        
        # 处理包含混合类型的列
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                # 尝试转换为日期类型
                try:
                    # 检查是否有足够的日期格式数据
                    sample = cleaned_df[col].dropna().astype(str).head(100)
                    date_count = sum(1 for val in sample if ExcelProcessor.is_date(val))
                    
                    if date_count > len(sample) * 0.7:  # 如果70%以上的值像是日期
                        cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                    else:
                        # 将所有object类型列转换为字符串，避免混合类型问题
                        cleaned_df[col] = cleaned_df[col].astype(str)
                        # 替换nan字符串
                        cleaned_df[col] = cleaned_df[col].replace('nan', '')
                except Exception as e:
                    logger.warning(f"列 '{col}' 日期转换失败: {str(e)}")
                    # 转换失败时，使用字符串
                    cleaned_df[col] = cleaned_df[col].astype(str)
                    cleaned_df[col] = cleaned_df[col].replace('nan', '')
        
        # 清理列名（移除特殊字符）
        clean_column_mapping = {}
        original_columns = cleaned_df.columns.tolist()
        
        for i, col in enumerate(original_columns):
            if pd.isna(col) or str(col).startswith('Unnamed:') or str(col).strip() == '':
                new_name = f"列{i+1}"
                clean_column_mapping[col] = new_name
                cleaned_df.rename(columns={col: new_name}, inplace=True)
            else:
                # 即使是正常列名也记录，方便后续显示
                clean_column_mapping[col] = str(col)
        
        # 添加列映射信息
        cleaned_df.attrs['column_mapping'] = clean_column_mapping
        
        return cleaned_df

    @staticmethod
    def validate_data(df):
        """
        验证数据质量和完整性
        
        Args:
            df: DataFrame对象
            
        Returns:
            dict: 验证结果
        """
        if df is None or df.empty:
            return {'status': 'error', 'message': '数据为空'}
        
        validation_results = []
        
        # 检查行数
        if df.shape[0] == 0:
            validation_results.append({
                'status': 'error',
                'message': '文件不包含任何数据行'
            })
        elif df.shape[0] < 5:
            validation_results.append({
                'status': 'warning',
                'message': f'文件只包含 {df.shape[0]} 行数据，可能不足以进行有意义的分析'
            })
        else:
            validation_results.append({
                'status': 'success',
                'message': f'文件包含 {df.shape[0]} 行数据，足够进行分析'
            })
        
        # 检查列数
        if df.shape[1] == 0:
            validation_results.append({
                'status': 'error',
                'message': '文件不包含任何数据列'
            })
        elif df.shape[1] < 2:
            validation_results.append({
                'status': 'warning',
                'message': '文件只包含1列数据，可能无法进行关联分析'
            })
        else:
            validation_results.append({
                'status': 'success',
                'message': f'文件包含 {df.shape[1]} 列数据'
            })
        
        # 检查数据类型
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            validation_results.append({
                'status': 'warning',
                'message': '文件不包含数值类型列，可能无法进行数值分析'
            })
        else:
            validation_results.append({
                'status': 'success',
                'message': f'文件包含 {len(numeric_cols)} 个数值类型列，可以进行数值分析'
            })
        
        # 检查缺失值
        missing_values = df.isnull().sum().sum()
        if missing_values > 0:
            missing_pct = (missing_values / (df.shape[0] * df.shape[1])) * 100
            if missing_pct > 50:
                validation_results.append({
                    'status': 'error',
                    'message': f'文件包含大量缺失值 ({missing_pct:.1f}%)，可能影响分析质量'
                })
            elif missing_pct > 20:
                validation_results.append({
                    'status': 'warning',
                    'message': f'文件包含较多缺失值 ({missing_pct:.1f}%)，可能需要数据清理'
                })
            else:
                validation_results.append({
                    'status': 'warning',
                    'message': f'文件包含少量缺失值 ({missing_pct:.1f}%)，分析时将自动处理'
                })
        else:
            validation_results.append({
                'status': 'success',
                'message': '文件不包含缺失值，数据完整'
            })
        
        # 检查异常值（针对数值列）
        if len(numeric_cols) > 0:
            outlier_cols = []
            for col in numeric_cols:
                # 使用IQR方法检测异常值
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outlier_count = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                outlier_pct = (outlier_count / len(df)) * 100
                
                if outlier_pct > 10:
                    outlier_cols.append((col, outlier_pct))
            
            if outlier_cols:
                validation_results.append({
                    'status': 'warning',
                    'message': f'检测到 {len(outlier_cols)} 列包含较多异常值，可能需要处理',
                    'details': {col: f"{pct:.1f}%" for col, pct in outlier_cols}
                })
        
        # 检查重复行
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            duplicate_pct = (duplicate_count / len(df)) * 100
            validation_results.append({
                'status': 'warning',
                'message': f'文件包含 {duplicate_count} 行重复数据 ({duplicate_pct:.1f}%)'
            })
        
        return validation_results

    @staticmethod
    def get_sheet_info(uploaded_file, detailed=False):
        """
        获取Excel文件中所有工作表的信息
        
        Args:
            uploaded_file: 上传的Excel文件对象
            detailed: 是否获取详细信息
            
        Returns:
            list: 工作表信息列表
        """
        if uploaded_file is None:
            return []
        
        try:
            # 读取Excel文件
            excel_file = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
            sheet_names = excel_file.sheet_names
            
            # 收集每个工作表的基本信息
            sheets_info = []
            
            for sheet in sheet_names:
                try:
                    # 只读取头部数据以获取基本信息
                    df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), sheet_name=sheet, nrows=10 if detailed else 5)
                    
                    sheet_info = {
                        'name': sheet,
                        'columns': len(df.columns),
                        'preview_rows': len(df),
                        'column_names': df.columns.tolist()[:10 if detailed else 5]  # 显示前5或10个列名
                    }
                    
                    # 如果需要详细信息，添加更多数据
                    if detailed:
                        # 获取数据类型信息
                        dtypes = {}
                        for col in df.columns:
                            dtype = str(df[col].dtype)
                            if dtype == 'object':
                                # 尝试检测更具体的类型
                                sample = df[col].dropna().astype(str).head(100)
                                date_count = sum(1 for val in sample if ExcelProcessor.is_date(val))
                                if date_count > len(sample) * 0.7:
                                    dtypes[col] = 'date'
                                else:
                                    dtypes[col] = 'text'
                            elif 'int' in dtype or 'float' in dtype:
                                dtypes[col] = 'numeric'
                            else:
                                dtypes[col] = dtype
                        
                        sheet_info['column_types'] = dtypes
                        
                        # 获取缺失值信息
                        missing_values = df.isnull().sum().to_dict()
                        sheet_info['missing_values'] = {col: count for col, count in missing_values.items() if count > 0}
                        
                        # 获取行数估计（不读取全部数据，可能不准确）
                        try:
                            # 尝试获取工作表的行数（不读取数据）
                            row_count = excel_file.book.sheet_by_name(sheet).nrows - 1  # 减去标题行
                            sheet_info['estimated_rows'] = max(0, row_count)
                        except:
                            sheet_info['estimated_rows'] = "未知"
                    
                    sheets_info.append(sheet_info)
                except Exception as e:
                    logger.warning(f"读取工作表 '{sheet}' 信息失败: {str(e)}")
                    sheets_info.append({
                        'name': sheet,
                        'error': str(e)
                    })
            
            return sheets_info
            
        except Exception as e:
            logger.error(f"获取工作表信息时出错: {str(e)}")
            raise Exception(f"获取工作表信息时出错: {str(e)}")

    @staticmethod
    def get_data_summary(df):
        """
        生成数据摘要统计
        
        Args:
            df: DataFrame对象
            
        Returns:
            dict: 数据摘要统计
        """
        if df is None or df.empty:
            return {'error': '没有数据可供分析'}
        
        try:
            summary = {
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.astype(str).to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'numeric_summary': {},
                'categorical_summary': {},
                'date_summary': {}
            }
            
            # 数值列统计
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                numeric_summary = df[numeric_cols].describe().to_dict()
                
                # 添加额外的统计信息
                for col in numeric_cols:
                    # 添加中位数绝对偏差(MAD)，用于异常值检测
                    median = df[col].median()
                    mad = (df[col] - median).abs().median()
                    
                    # 添加偏度和峰度
                    skew = df[col].skew()
                    kurtosis = df[col].kurtosis()
                    
                    # 添加到摘要
                    if col in numeric_summary:
                        numeric_summary[col]['mad'] = mad
                        numeric_summary[col]['skew'] = skew
                        numeric_summary[col]['kurtosis'] = kurtosis
                
                summary['numeric_summary'] = numeric_summary
            
            # 分类列统计
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                cat_summary = {}
                for col in categorical_cols:
                    value_counts = df[col].value_counts().head(10).to_dict()  # 取前10个最常见值
                    unique_count = df[col].nunique()
                    cat_summary[col] = {
                        'unique_count': unique_count,
                        'top_values': value_counts,
                        'coverage': sum(value_counts.values()) / len(df) * 100  # 前10个值覆盖的数据百分比
                    }
                summary['categorical_summary'] = cat_summary
            
            # 日期列统计
            date_cols = df.select_dtypes(include=['datetime']).columns
            if len(date_cols) > 0:
                date_summary = {}
                for col in date_cols:
                    try:
                        min_date = df[col].min()
                        max_date = df[col].max()
                        date_range = (max_date - min_date).days
                        
                        # 计算日期分布
                        if isinstance(min_date, pd.Timestamp) and isinstance(max_date, pd.Timestamp):
                            date_summary[col] = {
                                'min_date': min_date.strftime('%Y-%m-%d'),
                                'max_date': max_date.strftime('%Y-%m-%d'),
                                'date_range_days': date_range,
                                'missing_count': df[col].isnull().sum()
                            }
                            
                            # 添加按年/月/日的分布
                            if date_range > 365:  # 如果跨度超过一年，按年统计
                                year_counts = df[col].dt.year.value_counts().sort_index().to_dict()
                                date_summary[col]['year_distribution'] = year_counts
                            elif date_range > 30:  # 如果跨度超过一个月，按月统计
                                df['temp_month'] = df[col].dt.strftime('%Y-%m')
                                month_counts = df['temp_month'].value_counts().sort_index().head(12).to_dict()
                                del df['temp_month']
                                date_summary[col]['month_distribution'] = month_counts
                            else:  # 否则按日统计
                                df['temp_day'] = df[col].dt.strftime('%Y-%m-%d')
                                day_counts = df['temp_day'].value_counts().sort_index().head(30).to_dict()
                                del df['temp_day']
                                date_summary[col]['day_distribution'] = day_counts
                    except Exception as e:
                        logger.warning(f"处理日期列 '{col}' 时出错: {str(e)}")
                        date_summary[col] = {'error': str(e)}
                
                summary['date_summary'] = date_summary
            
            # 相关性分析（仅对数值列）
            if len(numeric_cols) > 1:
                try:
                    corr_matrix = df[numeric_cols].corr().round(2).to_dict()
                    # 找出高相关性对
                    high_correlations = []
                    for i, col1 in enumerate(numeric_cols):
                        for j, col2 in enumerate(numeric_cols):
                            if i < j:  # 避免重复
                                corr = corr_matrix.get(col1, {}).get(col2, 0)
                                if abs(corr) > 0.7:  # 高相关性阈值
                                    high_correlations.append({
                                        'columns': [col1, col2],
                                        'correlation': corr
                                    })
                    
                    summary['correlations'] = {
                        'matrix': corr_matrix,
                        'high_correlations': high_correlations
                    }
                except Exception as e:
                    logger.warning(f"计算相关性时出错: {str(e)}")
            
            return summary
            
        except Exception as e:
            logger.error(f"生成数据摘要时出错: {str(e)}")
            return {'error': f"生成数据摘要时出错: {str(e)}"}

    @staticmethod
    def filter_dataframe(df, filters):
        """
        根据过滤条件筛选DataFrame
        
        Args:
            df: DataFrame对象
            filters: 过滤条件字典
            
        Returns:
            pd.DataFrame: 过滤后的DataFrame
        """
        if df is None or df.empty or not filters:
            return df
        
        filtered_df = df.copy()
        
        try:
            # 应用数值范围过滤
            for col, range_values in filters.get('numeric_ranges', {}).items():
                if col in filtered_df.columns:
                    min_val, max_val = range_values
                    filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]
            
            # 应用分类值过滤
            for col, selected_values in filters.get('categorical_values', {}).items():
                if col in filtered_df.columns and selected_values:
                    filtered_df = filtered_df[filtered_df[col].isin(selected_values)]
            
            # 应用文本搜索过滤
            for col, search_text in filters.get('text_search', {}).items():
                if col in filtered_df.columns and search_text:
                    filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(search_text, case=False, na=False)]
            
            # 应用日期范围过滤
            for col, date_range in filters.get('date_ranges', {}).items():
                if col in filtered_df.columns:
                    start_date, end_date = date_range
                    if start_date:
                        filtered_df = filtered_df[filtered_df[col] >= start_date]
                    if end_date:
                        filtered_df = filtered_df[filtered_df[col] <= end_date]
            
            # 应用缺失值过滤
            if filters.get('missing_filter'):
                for col, action in filters.get('missing_filter').items():
                    if col in filtered_df.columns:
                        if action == 'remove':
                            filtered_df = filtered_df.dropna(subset=[col])
                        elif action == 'keep_only':
                            filtered_df = filtered_df[filtered_df[col].isna()]
            
            # 应用排序
            if filters.get('sort'):
                col = filters.get('sort').get('column')
                ascending = filters.get('sort').get('ascending', True)
                if col in filtered_df.columns:
                    filtered_df = filtered_df.sort_values(by=col, ascending=ascending)
            
            return filtered_df
            
        except Exception as e:
            logger.error(f"过滤数据时出错: {str(e)}")
            raise Exception(f"过滤数据时出错: {str(e)}")

    @staticmethod
    def detect_data_types(df):
        """
        检测DataFrame中各列的数据类型和特征
        
        Args:
            df: DataFrame对象
            
        Returns:
            dict: 列数据类型和特征
        """
        if df is None or df.empty:
            return {}
        
        column_types = {}
        
        for col in df.columns:
            col_type = str(df[col].dtype)
            
            # 基本类型检测
            if df[col].dtype in ['int64', 'float64']:
                data_type = 'numeric'
            elif df[col].dtype == 'datetime64[ns]':
                data_type = 'date'
            elif df[col].dtype == 'object':
                # 进一步检测字符串列的特征
                sample = df[col].dropna().astype(str).head(100)
                
                # 检测日期
                date_count = sum(1 for val in sample if ExcelProcessor.is_date(val))
                
                if date_count > len(sample) * 0.7:  # 如果70%以上的值像是日期
                    data_type = 'date'
                else:
                    # 检测分类变量
                    unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
                    if unique_ratio < 0.2:  # 如果唯一值比例小于20%
                        data_type = 'categorical'
                    else:
                        data_type = 'text'
            else:
                data_type = 'other'
            
            # 收集列统计信息
            stats = {
                'raw_type': col_type,
                'detected_type': data_type,
                'unique_count': df[col].nunique(),
                'missing_count': df[col].isnull().sum(),
                'missing_pct': df[col].isnull().sum() / len(df) * 100 if len(df) > 0 else 0
            }
            
            # 根据数据类型添加特定统计信息
            if data_type == 'numeric':
                stats.update({
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'mean': df[col].mean(),
                    'median': df[col].median(),
                    'std': df[col].std()
                })
            elif data_type == 'categorical' or data_type == 'text':
                # 获取前5个最常见值及其频率
                value_counts = df[col].value_counts().head(5).to_dict()
                stats['top_values'] = value_counts
            elif data_type == 'date':
                try:
                    # 如果是字符串日期，先转换
                    if df[col].dtype == 'object':
                        date_series = pd.to_datetime(df[col], errors='coerce')
                    else:
                        date_series = df[col]
                    
                    stats.update({
                        'min_date': date_series.min(),
                        'max_date': date_series.max(),
                        'date_range_days': (date_series.max() - date_series.min()).days if not pd.isna(date_series.min()) and not pd.isna(date_series.max()) else None
                    })
                except Exception as e:
                    logger.warning(f"处理日期列 '{col}' 时出错: {str(e)}")
            
            column_types[col] = stats
        
        return column_types

    @staticmethod
    def is_date(string):
        """
        检查字符串是否可能是日期
        
        Args:
            string: 要检查的字符串
            
        Returns:
            bool: 是否可能是日期
        """
        # 常见日期格式的正则表达式
        date_patterns = [
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # YYYY-MM-DD or YYYY/MM/DD
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # DD-MM-YYYY or MM-DD-YYYY
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2}',  # DD-MM-YY or MM-DD-YY
            r'\d{4}年\d{1,2}月\d{1,2}日',    # 中文日期格式
            r'\d{1,2}/\d{1,2}/\d{2,4}',      # MM/DD/YY or MM/DD/YYYY
        ]
        
        # 检查是否匹配任何日期模式
        for pattern in date_patterns:
            if re.match(pattern, string):
                return True
        
        # 尝试使用pandas解析
        try:
            pd.to_datetime(string)
            return True
        except:
            return False
    
    @staticmethod
    def clean_column_names(df):
        """
        清理和标准化列名
        
        Args:
            df: DataFrame对象
            
        Returns:
            pd.DataFrame: 具有清理后列名的DataFrame
        """
        if df is None or df.empty:
            return df
        
        cleaned_df = df.copy()
        
        # 创建列名映射
        column_mapping = {}
        
        for i, col in enumerate(cleaned_df.columns):
            # 处理空列名或未命名列
            if pd.isna(col) or str(col).startswith('Unnamed:') or str(col).strip() == '':
                new_name = f"column_{i+1}"
                column_mapping[col] = new_name
            else:
                # 清理列名中的特殊字符
                new_name = str(col)
                # 替换空格和特殊字符为下划线
                new_name = re.sub(r'[^\w\s]', '_', new_name)
                new_name = re.sub(r'\s+', '_', new_name)
                # 确保列名不以数字开头
                if re.match(r'^\d', new_name):
                    new_name = f"col_{new_name}"
                # 确保列名唯一
                if new_name in column_mapping.values():
                    j = 1
                    while f"{new_name}_{j}" in column_mapping.values():
                        j += 1
                    new_name = f"{new_name}_{j}"
                
                column_mapping[col] = new_name
        
        # 重命名列
        cleaned_df.rename(columns=column_mapping, inplace=True)
        
        # 存储原始列名映射
        cleaned_df.attrs['original_columns'] = column_mapping
        
        return cleaned_df
    
    @staticmethod
    def handle_missing_values(df, strategy='auto'):
        """
        处理缺失值
        
        Args:
            df: DataFrame对象
            strategy: 处理策略 ('auto', 'drop', 'mean', 'median', 'mode', 'zero', 'none')
            
        Returns:
            pd.DataFrame: 处理后的DataFrame
        """
        if df is None or df.empty:
            return df
        
        # 创建副本
        result_df = df.copy()
        
        # 记录处理操作
        operations = {}
        
        # 根据策略处理缺失值
        if strategy == 'drop':
            # 删除包含缺失值的行
            original_rows = len(result_df)
            result_df = result_df.dropna()
            operations['dropped_rows'] = original_rows - len(result_df)
            
        elif strategy == 'none':
            # 不处理缺失值
            pass
            
        else:  # 'auto', 'mean', 'median', 'mode', 'zero'
            for col in result_df.columns:
                missing_count = result_df[col].isnull().sum()
                
                if missing_count == 0:
                    continue
                
                # 记录原始缺失值数量
                operations[col] = {'missing_count': missing_count}
                
                # 根据数据类型和策略选择填充方法
                if result_df[col].dtype in ['int64', 'float64']:
                    if strategy == 'auto' or strategy == 'mean':
                        fill_value = result_df[col].mean()
                        operations[col]['strategy'] = 'mean'
                    elif strategy == 'median':
                        fill_value = result_df[col].median()
                        operations[col]['strategy'] = 'median'
                    elif strategy == 'zero':
                        fill_value = 0
                        operations[col]['strategy'] = 'zero'
                    else:  # mode
                        fill_value = result_df[col].mode()[0] if not result_df[col].mode().empty else 0
                        operations[col]['strategy'] = 'mode'
                    
                    result_df[col].fillna(fill_value, inplace=True)
                    operations[col]['fill_value'] = fill_value
                    
                elif result_df[col].dtype == 'object':
                    if strategy == 'auto' or strategy == 'mode':
                        # 使用最常见值填充
                        if not result_df[col].mode().empty:
                            fill_value = result_df[col].mode()[0]
                            result_df[col].fillna(fill_value, inplace=True)
                            operations[col]['strategy'] = 'mode'
                            operations[col]['fill_value'] = fill_value
                        else:
                            # 如果没有最常见值，使用空字符串
                            result_df[col].fillna('', inplace=True)
                            operations[col]['strategy'] = 'empty_string'
                            operations[col]['fill_value'] = ''
                    else:
                        # 其他策略使用空字符串
                        result_df[col].fillna('', inplace=True)
                        operations[col]['strategy'] = 'empty_string'
                        operations[col]['fill_value'] = ''
                
                elif pd.api.types.is_datetime64_dtype(result_df[col]):
                    if strategy == 'auto':
                        # 对于日期，使用中位数填充
                        if not result_df[col].median() is pd.NaT:
                            fill_value = result_df[col].median()
                            result_df[col].fillna(fill_value, inplace=True)
                            operations[col]['strategy'] = 'median_date'
                            operations[col]['fill_value'] = fill_value
                    else:
                        # 其他策略不处理日期缺失值
                        operations[col]['strategy'] = 'no_action'
        
        # 存储处理操作
        result_df.attrs['missing_value_operations'] = operations
        
        return result_df
    
    @staticmethod
    def detect_outliers(df, method='iqr', threshold=1.5):
        """
        检测异常值
        
        Args:
            df: DataFrame对象
            method: 检测方法 ('iqr', 'zscore')
            threshold: 阈值
            
        Returns:
            dict: 异常值信息
        """
        if df is None or df.empty:
            return {}
        
        outliers = {}
        
        # 只对数值列进行异常值检测
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            if method == 'iqr':
                # IQR方法
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outlier_count = outlier_mask.sum()
                
                if outlier_count > 0:
                    outliers[col] = {
                        'method': 'iqr',
                        'count': outlier_count,
                        'percentage': outlier_count / len(df) * 100,
                        'bounds': (lower_bound, upper_bound),
                        'indices': df.index[outlier_mask].tolist()[:100]  # 限制返回的索引数量
                    }
            
            elif method == 'zscore':
                # Z-score方法
                mean = df[col].mean()
                std = df[col].std()
                
                if std > 0:  # 避免除以零
                    z_scores = (df[col] - mean) / std
                    outlier_mask = abs(z_scores) > threshold
                    outlier_count = outlier_mask.sum()
                    
                    if outlier_count > 0:
                        outliers[col] = {
                            'method': 'zscore',
                            'count': outlier_count,
                            'percentage': outlier_count / len(df) * 100,
                            'threshold': threshold,
                            'indices': df.index[outlier_mask].tolist()[:100]  # 限制返回的索引数量
                        }
        
        return outliers
    
    @staticmethod
    def convert_column_types(df, conversions):
        """
        转换列数据类型
        
        Args:
            df: DataFrame对象
            conversions: 转换配置字典 {列名: 目标类型}
            
        Returns:
            pd.DataFrame: 转换后的DataFrame
        """
        if df is None or df.empty or not conversions:
            return df
        
        result_df = df.copy()
        conversion_results = {}
        
        for col, target_type in conversions.items():
            if col not in result_df.columns:
                conversion_results[col] = {'status': 'error', 'message': '列不存在'}
                continue
            
            try:
                if target_type == 'numeric':
                    # 转换为数值类型
                    result_df[col] = pd.to_numeric(result_df[col], errors='coerce')
                    conversion_results[col] = {'status': 'success', 'type': str(result_df[col].dtype)}
                
                elif target_type == 'date':
                    # 转换为日期类型
                    result_df[col] = pd.to_datetime(result_df[col], errors='coerce')
                    conversion_results[col] = {'status': 'success', 'type': str(result_df[col].dtype)}
                
                elif target_type == 'category':
                    # 转换为分类类型
                    result_df[col] = result_df[col].astype('category')
                    conversion_results[col] = {'status': 'success', 'type': str(result_df[col].dtype)}
                
                elif target_type == 'string':
                    # 转换为字符串类型
                    result_df[col] = result_df[col].astype(str)
                    conversion_results[col] = {'status': 'success', 'type': str(result_df[col].dtype)}
                
                else:
                    # 尝试直接转换为指定类型
                    result_df[col] = result_df[col].astype(target_type)
                    conversion_results[col] = {'status': 'success', 'type': str(result_df[col].dtype)}
                
            except Exception as e:
                conversion_results[col] = {'status': 'error', 'message': str(e)}
        
        # 存储转换结果
        result_df.attrs['type_conversions'] = conversion_results
        
        return result_df

# 导出便捷函数
def process_excel_file(uploaded_file, sheet_name=None):
    """处理上传的Excel文件"""
    return ExcelProcessor.process_excel_file(uploaded_file, sheet_name)

def clean_dataframe(df):
    """清理DataFrame，处理混合类型和特殊字符"""
    return ExcelProcessor.clean_dataframe(df)

def get_sheet_info(uploaded_file, detailed=False):
    """获取Excel文件中所有工作表的信息"""
    return ExcelProcessor.get_sheet_info(uploaded_file, detailed)

def get_data_summary(df):
    """生成数据摘要统计"""
    return ExcelProcessor.get_data_summary(df)

def filter_dataframe(df, filters):
    """根据过滤条件筛选DataFrame"""
    return ExcelProcessor.filter_dataframe(df, filters)

def detect_data_types(df):
    """检测DataFrame中各列的数据类型和特征"""
    return ExcelProcessor.detect_data_types(df)

def is_date(string):
    """检查字符串是否可能是日期"""
    return ExcelProcessor.is_date(string)

def clean_column_names(df):
    """清理和标准化列名"""
    return ExcelProcessor.clean_column_names(df)

def handle_missing_values(df, strategy='auto'):
    """处理缺失值"""
    return ExcelProcessor.handle_missing_values(df, strategy)

def detect_outliers(df, method='iqr', threshold=1.5):
    """检测异常值"""
    return ExcelProcessor.detect_outliers(df, method, threshold)

def convert_column_types(df, conversions):
    """转换列数据类型"""
    return ExcelProcessor.convert_column_types(df, conversions)

def validate_data(df):
    """验证数据质量和完整性"""
    return ExcelProcessor.validate_data(df)