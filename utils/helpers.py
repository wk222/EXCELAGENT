#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 辅助函数

通用辅助函数和工具
"""

import streamlit as st
import pandas as pd
import plotly.io as pio
import base64
import io
import json
import os
import datetime

def get_table_download_link(df, filename="data.csv", text="下载CSV"):
    """
    生成DataFrame下载链接
    
    Args:
        df: DataFrame对象
        filename: 下载文件名
        text: 链接文本
        
    Returns:
        str: HTML下载链接
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def get_chart_download_link(fig, filename="chart.html", text="下载图表"):
    """
    生成Plotly图表下载链接
    
    Args:
        fig: Plotly图表对象
        filename: 下载文件名
        text: 链接文本
        
    Returns:
        str: HTML下载链接
    """
    html = pio.to_html(fig)
    b64 = base64.b64encode(html.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}">{text}</a>'
    return href

def format_number(num):
    """
    格式化数字显示
    
    Args:
        num: 要格式化的数字
        
    Returns:
        str: 格式化后的数字字符串
    """
    if num is None:
        return "N/A"
    
    if isinstance(num, (int, float)):
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        elif isinstance(num, float):
            return f"{num:.2f}"
        else:
            return str(num)
    
    return str(num)

def apply_theme(theme):
    """
    应用主题样式
    
    Args:
        theme: 主题名称 ('light' 或 'dark')
    """
    if theme == "light":
        # 浅色主题
        st.markdown("""
        <style>
            /* 全局背景和文本 */
            .stApp {
                background-color: #f8f9fa;
                color: #333333;
            }
            
            /* 标题样式 */
            .main-header {
                color: #1f77b4;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #1f77b4;
            }
            
            /* 侧边栏样式 */
            .stSidebar {
                background-color: #ffffff;
                border-right: 1px solid #e9ecef;
            }
            
            /* 卡片和容器样式 */
            .stBlock {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 0.5rem;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            /* 按钮样式 */
            .stButton>button {
                background-color: #1f77b4;
                color: white;
                border: none;
                border-radius: 0.25rem;
                padding: 0.5rem 1rem;
                font-weight: 500;
            }
            
            .stButton>button:hover {
                background-color: #1a6eaa;
            }
            
            /* 输入框样式 */
            .stTextInput>div>div>input, .stNumberInput>div>div>input {
                border: 1px solid #ced4da;
                border-radius: 0.25rem;
                padding: 0.5rem;
            }
            
            /* 选择框样式 */
            .stSelectbox>div>div>div {
                border: 1px solid #ced4da;
                border-radius: 0.25rem;
            }
            
            /* 滑块样式 */
            .stSlider>div>div>div>div>div {
                background-color: #1f77b4;
            }
            
            /* 链接样式 */
            a {
                color: #1f77b4;
                text-decoration: none;
            }
            
            a:hover {
                text-decoration: underline;
            }
            
            /* 表格样式 */
            .stDataFrame {
                border: 1px solid #e9ecef;
            }
            
            .stDataFrame th {
                background-color: #f8f9fa;
                color: #333333;
                font-weight: 500;
            }
            
            /* 提示信息样式 */
            .stAlert {
                border-radius: 0.25rem;
            }
        </style>
        """, unsafe_allow_html=True)
    else:  # dark theme
        # 深色主题
        st.markdown("""
        <style>
            /* 全局背景和文本 */
            .stApp {
                background-color: #0e1117;
                color: #f8f9fa;
            }
            
            /* 标题样式 */
            .main-header {
                color: #4da6ff;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #4da6ff;
            }
            
            /* 侧边栏样式 */
            .stSidebar {
                background-color: #262730;
                border-right: 1px solid #4a4b56;
            }
            
            /* 卡片和容器样式 */
            .stBlock {
                background-color: #262730;
                border: 1px solid #4a4b56;
                border-radius: 0.5rem;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            /* 按钮样式 */
            .stButton>button {
                background-color: #4da6ff;
                color: white;
                border: none;
                border-radius: 0.25rem;
                padding: 0.5rem 1rem;
                font-weight: 500;
            }
            
            .stButton>button:hover {
                background-color: #3a93ff;
            }
            
            /* 输入框样式 */
            .stTextInput>div>div>input, .stNumberInput>div>div>input {
                background-color: #3a3b47;
                border: 1px solid #4a4b56;
                color: #f8f9fa;
                border-radius: 0.25rem;
                padding: 0.5rem;
            }
            
            /* 选择框样式 */
            .stSelectbox>div>div>div {
                background-color: #3a3b47;
                border: 1px solid #4a4b56;
                color: #f8f9fa;
                border-radius: 0.25rem;
            }
            
            /* 滑块样式 */
            .stSlider>div>div>div>div>div {
                background-color: #4da6ff;
            }
            
            /* 链接样式 */
            a {
                color: #4da6ff;
                text-decoration: none;
            }
            
            a:hover {
                text-decoration: underline;
            }
            
            /* 表格样式 */
            .stDataFrame {
                border: 1px solid #4a4b56;
            }
            
            .stDataFrame th {
                background-color: #3a3b47;
                color: #f8f9fa;
                font-weight: 500;
            }
            
            /* 提示信息样式 */
            .stAlert {
                border-radius: 0.25rem;
            }
            
            /* 代码块样式 */
            .stCodeBlock {
                background-color: #1e1e1e;
                border: 1px solid #4a4b56;
            }
        </style>
        """, unsafe_allow_html=True)

def get_current_time_str():
    """
    获取当前时间字符串
    
    Returns:
        str: 格式化的当前时间字符串
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def save_uploaded_file(uploaded_file, save_dir="temp"):
    """
    保存上传的文件
    
    Args:
        uploaded_file: 上传的文件对象
        save_dir: 保存目录
        
    Returns:
        str: 保存的文件路径
    """
    # 确保目录存在
    os.makedirs(save_dir, exist_ok=True)
    
    # 构建文件路径
    file_path = os.path.join(save_dir, uploaded_file.name)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def load_json_file(file_path):
    """
    加载JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        dict: JSON数据
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"加载JSON文件失败: {str(e)}")
        return {}

def save_json_file(data, file_path):
    """
    保存JSON文件
    
    Args:
        data: 要保存的数据
        file_path: 保存路径
        
    Returns:
        bool: 是否保存成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存JSON文件失败: {str(e)}")
        return False

def truncate_text(text, max_length=100):
    """
    截断文本
    
    Args:
        text: 要截断的文本
        max_length: 最大长度
        
    Returns:
        str: 截断后的文本
    """
    if text and len(text) > max_length:
        return text[:max_length] + "..."
    return text