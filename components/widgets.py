#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - UI组件

可重用的UI组件
"""

import streamlit as st
import pandas as pd
import io
import plotly.io as pio
import base64
from state import get_ui_preferences

# 应用全局样式 - 已移至 utils/styling.py
def apply_global_styles():
    """应用全局样式 - 此函数已移至 utils/styling.py，保留此处以兼容现有代码"""
    from utils.styling import apply_global_styles as apply_styles
    apply_styles()

# 文件上传组件
def file_uploader_card():
    """文件上传卡片组件"""
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📁 上传Excel文件</div>', unsafe_allow_html=True)
        
        # 文件上传区域
        col1, col2 = st.columns([3, 2])
        
        with col1:
            uploaded_file = st.file_uploader(
                "上传Excel文件",
                type=["xlsx", "xls"],
                help="支持.xlsx和.xls格式",
                key="excel_uploader"
            )
        
        with col2:
            st.markdown("""
            ### 支持的格式
            - Microsoft Excel (.xlsx)
            - 旧版Excel (.xls)
            
            ### 文件要求
            - 最大文件大小: 200MB
            - 包含有效的数据表
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return uploaded_file

# 分析阶段卡片组件
def stage_card(title, status, content_func):
    """分析阶段卡片组件"""
    status_classes = {
        "pending": "stage-pending",
        "in_progress": "stage-in-progress",
        "completed": "stage-completed",
        "error": "stage-error"
    }
    
    status_badges = {
        "pending": '<span class="status-badge status-pending">⏳ 待执行</span>',
        "in_progress": '<span class="status-badge status-in-progress">🔄 执行中</span>',
        "completed": '<span class="status-badge status-completed">✅ 已完成</span>',
        "error": '<span class="status-badge status-error">❌ 错误</span>'
    }
    
    with st.container():
        st.markdown(f'<div class="card stage-card {status_classes.get(status, "")}">', unsafe_allow_html=True)
        
        # 卡片标题和状态
        st.markdown(f'<div class="card-header">{title} {status_badges.get(status, "")}</div>', unsafe_allow_html=True)
        
        # 卡片内容
        content_func()
        
        st.markdown('</div>', unsafe_allow_html=True)

# 数据预览卡片组件
def data_preview_card(df, max_rows=5):
    """数据预览卡片组件"""
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📋 数据预览</div>', unsafe_allow_html=True)
        
        if df is not None and not df.empty:
            # 显示基本信息
            col1, col2, col3 = st.columns(3)
            with col1:
                metric_card("行数", df.shape[0])
            with col2:
                metric_card("列数", df.shape[1])
            with col3:
                metric_card("数据类型", len(df.dtypes.unique()))
            
            # 显示列信息
            with st.expander("📊 列信息", expanded=True):
                col_info = []
                for i, col in enumerate(df.columns):
                    dtype = str(df[col].dtype)
                    non_null = df[col].count()
                    null_count = df[col].isnull().sum()
                    null_pct = (null_count / len(df)) * 100
                    
                    col_info.append(f"• **{col}** ({dtype}) - {non_null} 非空值, {null_count} 缺失值 ({null_pct:.1f}%)")
                st.markdown("\n".join(col_info))
            
            # 显示数据预览
            with st.expander("👀 数据预览", expanded=True):
                st.dataframe(df.head(max_rows), use_container_width=True)
                
                # 下载按钮
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 下载数据 (CSV)",
                    data=csv,
                    file_name="data.csv",
                    mime="text/csv",
                )
        else:
            st.warning("没有数据可供预览")
        
        st.markdown('</div>', unsafe_allow_html=True)

# 图表显示卡片组件
def chart_display_card(chart_json, title=None, description=None):
    """图表显示卡片组件"""
    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if title:
            st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
        
        if description:
            st.markdown(f'<div class="chart-description">{description}</div>', unsafe_allow_html=True)
        
        try:
            fig = pio.from_json(chart_json)
            st.plotly_chart(fig, use_container_width=True)
            
            # 下载按钮
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.download_button(
                    label="📥 下载图表 (HTML)",
                    data=pio.to_html(fig),
                    file_name=f"{title or 'chart'}.html",
                    mime="text/html"
                )
            
            with col2:
                # 生成PNG图像
                img_bytes = fig.to_image(format="png", width=1200, height=800, scale=2)
                
                st.download_button(
                    label="📥 下载图表 (PNG)",
                    data=img_bytes,
                    file_name=f"{title or 'chart'}.png",
                    mime="image/png"
                )
        except Exception as e:
            st.error(f"图表显示失败: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# 代码显示卡片组件
def code_display_card(code, language="python", title="生成的代码"):
    """代码显示卡片组件"""
    with st.container():
        st.markdown('<div class="code-block">', unsafe_allow_html=True)
        
        # 代码标题和操作按钮
        st.markdown(f"""
        <div class="code-header">
            <div class="code-title">{title}</div>
            <div class="code-actions">
                <button class="code-action-button" onclick="navigator.clipboard.writeText(`{code.replace('`', '\\`')}`)">
                    📋 复制
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 代码内容
        st.code(code, language=language)
        
        st.markdown('</div>', unsafe_allow_html=True)

# 设置卡片组件
def settings_card(title, settings_dict, on_save, description=None):
    """设置卡片组件"""
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-header">{title}</div>', unsafe_allow_html=True)
        
        if description:
            st.markdown(description)
        
        with st.form(f"settings_form_{title.lower().replace(' ', '_')}"):
            # 动态创建设置控件
            new_settings = {}
            
            for key, value in settings_dict.items():
                # 获取显示名称和帮助文本
                if isinstance(value, dict) and 'value' in value:
                    display_name = value.get('display_name', key)
                    help_text = value.get('help', '')
                    actual_value = value['value']
                else:
                    display_name = key
                    help_text = ''
                    actual_value = value
                
                # 根据值类型创建不同的控件
                if isinstance(actual_value, bool):
                    new_settings[key] = st.checkbox(display_name, value=actual_value, help=help_text)
                elif isinstance(actual_value, float):
                    if key.lower() in ['temperature', 'temp']:
                        # 温度参数特殊处理
                        new_settings[key] = st.slider(
                            display_name, 
                            min_value=0.0, 
                            max_value=1.0, 
                            value=actual_value, 
                            step=0.1,
                            help=help_text or "控制AI生成结果的创造性"
                        )
                    else:
                        new_settings[key] = st.number_input(
                            display_name, 
                            value=actual_value,
                            help=help_text
                        )
                elif isinstance(actual_value, int):
                    new_settings[key] = st.number_input(
                        display_name, 
                        value=actual_value,
                        step=1,
                        help=help_text
                    )
                elif isinstance(actual_value, list):
                    # 如果是列表，创建多选框
                    options = value.get('options', actual_value)
                    new_settings[key] = st.multiselect(
                        display_name,
                        options=options,
                        default=actual_value,
                        help=help_text
                    )
                elif key.lower() in ['password', 'api_key', 'secret']:
                    # 密码类型
                    new_settings[key] = st.text_input(
                        display_name,
                        value=actual_value,
                        type="password",
                        help=help_text
                    )
                else:
                    # 普通文本输入
                    new_settings[key] = st.text_input(
                        display_name,
                        value=actual_value,
                        help=help_text
                    )
            
            # 提交按钮
            col1, col2 = st.columns([3, 1])
            with col2:
                submitted = st.form_submit_button("保存设置", use_container_width=True)
            
            if submitted:
                on_save(new_settings)
                st.success("✅ 设置已更新")
        
        st.markdown('</div>', unsafe_allow_html=True)

# 错误显示卡片组件
def error_card(title, error_message, error_details=None):
    """错误显示卡片组件"""
    with st.container():
        st.markdown('<div class="card stage-error">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-header">❌ {title}</div>', unsafe_allow_html=True)
        
        st.error(error_message)
        
        if error_details:
            with st.expander("查看详细错误信息"):
                st.code(error_details)
        
        st.markdown('</div>', unsafe_allow_html=True)

# 成功显示卡片组件
def success_card(title, message, details=None):
    """成功显示卡片组件"""
    with st.container():
        st.markdown('<div class="card stage-completed">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-header">✅ {title}</div>', unsafe_allow_html=True)
        
        st.success(message)
        
        if details:
            with st.expander("查看详细信息"):
                st.write(details)
        
        st.markdown('</div>', unsafe_allow_html=True)

# 指标卡片组件
def metric_card(label, value, delta=None, help_text=None):
    """指标卡片组件"""
    # 格式化数值
    if isinstance(value, (int, float)):
        if value >= 1000000:
            formatted_value = f"{value/1000000:.1f}M"
        elif value >= 1000:
            formatted_value = f"{value/1000:.1f}K"
        elif isinstance(value, float):
            formatted_value = f"{value:.2f}"
        else:
            formatted_value = str(value)
    else:
        formatted_value = str(value)
    
    # 格式化增量
    delta_html = ""
    if delta is not None:
        if delta > 0:
            delta_html = f'<div style="color: #28a745">▲ {delta}</div>'
        elif delta < 0:
            delta_html = f'<div style="color: #dc3545">▼ {abs(delta)}</div>'
    
    # 渲染指标卡片
    st.markdown(f"""
    <div class="metric-card" title="{help_text or ''}">
        <div class="metric-value">{formatted_value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# 文件信息卡片组件
def file_info_card(file_data):
    """文件信息卡片组件"""
    if not file_data:
        return
    
    with st.container():
        st.markdown('<div class="file-info-card">', unsafe_allow_html=True)
        
        # 文件名和基本信息
        st.markdown(f'<div class="file-name">{file_data["filename"]}</div>', unsafe_allow_html=True)
        
        # 文件详情
        sheet_info = f"工作表: {file_data['current_sheet']}"
        if file_data.get('sheet_names') and len(file_data['sheet_names']) > 1:
            sheet_info += f" (共 {len(file_data['sheet_names'])} 个工作表)"
        
        size_info = f"{file_data['shape'][0]} 行 × {file_data['shape'][1]} 列"
        
        st.markdown(f'<div class="file-details">{sheet_info} | {size_info}</div>', unsafe_allow_html=True)
        
        # 工作表选择（如果有多个工作表）
        if file_data.get('sheet_names') and len(file_data['sheet_names']) > 1:
            selected_sheet = st.selectbox(
                "切换工作表",
                file_data['sheet_names'],
                index=file_data['sheet_names'].index(file_data['current_sheet']) if file_data['current_sheet'] in file_data['sheet_names'] else 0
            )
            
            if selected_sheet != file_data['current_sheet']:
                st.session_state.selected_sheet = selected_sheet
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# 进度指示器组件
def progress_steps(steps, current_step):
    """进度步骤指示器组件"""
    # 获取当前主题
    ui_prefs = get_ui_preferences()
    theme = ui_prefs.get('theme', 'light')
    
    # 根据主题设置颜色
    if theme == "light":
        active_color = "#1f77b4"
        inactive_color = "#e9ecef"
        text_color = "#333333"
    else:  # dark theme
        active_color = "#4da6ff"
        inactive_color = "#4a4b56"
        text_color = "#ffffff"
    
    # 生成进度步骤HTML
    html = f"""
    <style>
        .steps-container {{
            display: flex;
            justify-content: space-between;
            margin: 1rem 0 2rem 0;
            position: relative;
        }}
        
        .steps-container:before {{
            content: '';
            position: absolute;
            top: 15px;
            left: 0;
            right: 0;
            height: 2px;
            background: {inactive_color};
            z-index: 0;
        }}
        
        .step {{
            position: relative;
            z-index: 1;
            text-align: center;
        }}
        
        .step-circle {{
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: {inactive_color};
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem auto;
            font-weight: bold;
            color: white;
        }}
        
        .step-active .step-circle {{
            background-color: {active_color};
        }}
        
        .step-completed .step-circle {{
            background-color: {active_color};
        }}
        
        .step-completed .step-circle:after {{
            content: '✓';
        }}
        
        .step-label {{
            font-size: 0.8rem;
            color: {text_color};
            max-width: 100px;
            margin: 0 auto;
        }}
        
        .step-active .step-label {{
            font-weight: bold;
            color: {active_color};
        }}
    </style>
    
    <div class="steps-container">
    """
    
    # 添加每个步骤
    for i, step in enumerate(steps):
        step_class = ""
        step_content = str(i + 1)
        
        if i + 1 < current_step:
            step_class = "step-completed"
            step_content = "✓"
        elif i + 1 == current_step:
            step_class = "step-active"
        
        html += f"""
        <div class="step {step_class}">
            <div class="step-circle">{step_content}</div>
            <div class="step-label">{step}</div>
        </div>
        """
    
    html += "</div>"
    
    st.markdown(html, unsafe_allow_html=True)

# 标签页组件
def custom_tabs(tabs_dict, key_prefix="tab"):
    """自定义标签页组件"""
    # 获取当前主题
    ui_prefs = get_ui_preferences()
    theme = ui_prefs.get('theme', 'light')
    
    # 根据主题设置颜色
    if theme == "light":
        active_bg = "#ffffff"
        inactive_bg = "#f8f9fa"
        active_text = "#1f77b4"
        inactive_text = "#6c757d"
        border_color = "#dee2e6"
    else:  # dark theme
        active_bg = "#262730"
        inactive_bg = "#1e1e1e"
        active_text = "#4da6ff"
        inactive_text = "#adb5bd"
        border_color = "#4a4b56"
    
    # 初始化选中的标签
    if f"{key_prefix}_selected" not in st.session_state:
        st.session_state[f"{key_prefix}_selected"] = list(tabs_dict.keys())[0]
    
    # 生成标签页HTML
    html = f"""
    <style>
        .custom-tabs {{
            display: flex;
            border-bottom: 1px solid {border_color};
            margin-bottom: 1rem;
        }}
        
        .custom-tab {{
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            border: 1px solid transparent;
            border-bottom: none;
            border-radius: 0.25rem 0.25rem 0 0;
            margin-right: 0.25rem;
            font-weight: 500;
        }}
        
        .custom-tab-active {{
            background-color: {active_bg};
            color: {active_text};
            border-color: {border_color};
            border-bottom: 2px solid {active_bg};
            margin-bottom: -1px;
        }}
        
        .custom-tab-inactive {{
            background-color: {inactive_bg};
            color: {inactive_text};
        }}
        
        .custom-tab-inactive:hover {{
            background-color: {active_bg};
            color: {active_text};
        }}
        
        .custom-tab-content {{
            padding: 1rem 0;
        }}
    </style>
    
    <div class="custom-tabs">
    """
    
    # 添加每个标签
    for i, (tab_id, tab_info) in enumerate(tabs_dict.items()):
        tab_class = "custom-tab-active" if st.session_state[f"{key_prefix}_selected"] == tab_id else "custom-tab-inactive"
        tab_label = tab_info.get('label', tab_id)
        tab_icon = tab_info.get('icon', '')
        
        html += f"""
        <div class="custom-tab {tab_class}" id="{key_prefix}_{tab_id}" 
             onclick="document.getElementById('{key_prefix}_{tab_id}_btn').click()">
            {tab_icon} {tab_label}
        </div>
        """
    
    html += "</div>"
    
    # 渲染标签栏
    st.markdown(html, unsafe_allow_html=True)
    
    # 创建隐藏按钮用于切换标签
    cols = st.columns(len(tabs_dict))
    for i, (tab_id, tab_info) in enumerate(tabs_dict.items()):
        with cols[i]:
            if st.button(f"选择{tab_id}", key=f"{key_prefix}_{tab_id}_btn", help=tab_info.get('help', ''), visible=False):
                st.session_state[f"{key_prefix}_selected"] = tab_id
                st.rerun()
    
    # 返回当前选中的标签ID
    return st.session_state[f"{key_prefix}_selected"]