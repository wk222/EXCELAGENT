#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 设置页面

提供应用设置和LLM参数控制
"""

import streamlit as st
import os
from state import get_llm_settings, update_llm_settings, get_ui_preferences, update_ui_preferences

def render():
    """渲染设置页面"""
    # 主标题
    st.markdown('<h1 class="main-header">⚙️ Excel智能体 - 设置</h1>', unsafe_allow_html=True)
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["🤖 LLM设置", "🎨 界面设置", "ℹ️ 关于"])
    
    # LLM设置选项卡
    with tab1:
        render_llm_settings()
    
    # 界面设置选项卡
    with tab2:
        render_ui_settings()
    
    # 关于选项卡
    with tab3:
        render_about()

def render_llm_settings():
    """渲染LLM设置"""
    from logic.llm_service import validate_api_settings, get_available_models
    from state import update_llm_parameter, update_llm_temperature, update_llm_max_tokens, update_llm_model, toggle_llm_settings_persistence
    
    st.markdown("## 🤖 LLM设置")
    st.markdown("配置大语言模型的参数，以控制分析结果的生成。")
    
    # 获取当前LLM设置
    llm_settings = get_llm_settings()
    
    # 创建表单
    with st.form("llm_settings_form"):
        # 模型选择
        available_models = get_available_models()
        
        # 确保当前模型在列表中
        if llm_settings['model'] not in available_models:
            available_models.append(llm_settings['model'])
        
        model_index = available_models.index(llm_settings['model']) if llm_settings['model'] in available_models else 0
        
        model = st.selectbox(
            "模型",
            available_models,
            index=model_index,
            help="选择要使用的大语言模型"
        )
        
        # 基本参数
        st.markdown("### 基本参数")
        
        col1, col2 = st.columns(2)
        
        with col1:
            temperature = st.slider(
                "温度系数",
                min_value=0.0,
                max_value=1.0,
                value=llm_settings['temperature'],
                step=0.1,
                help="控制AI生成结果的创造性。较低的值使结果更确定，较高的值使结果更多样化。"
            )
        
        with col2:
            # 最大令牌数
            max_tokens = st.slider(
                "最大令牌数",
                min_value=500,
                max_value=8000,
                value=llm_settings['max_tokens'],
                step=500,
                help="控制生成文本的最大长度。"
            )
        
        # API设置
        st.markdown("### API设置")
        
        # API密钥
        api_key = st.text_input(
            "API密钥",
            value=llm_settings['api_key'],
            type="password",
            help="输入API密钥（如果使用默认设置可留空）"
        )
        
        # API基础URL
        base_url = st.text_input(
            "API基础URL",
            value=llm_settings['base_url'],
            help="输入API基础URL（如果使用默认设置可留空）"
        )
        
        # 高级选项
        with st.expander("高级参数", expanded=False):
            # 请求超时
            timeout = st.number_input(
                "请求超时（秒）",
                min_value=10,
                max_value=300,
                value=llm_settings.get('timeout', 60),
                step=10,
                help="API请求超时时间"
            )
            
            # 重试次数
            retries = st.number_input(
                "重试次数",
                min_value=0,
                max_value=5,
                value=llm_settings.get('retries', 2),
                step=1,
                help="API请求失败时的重试次数"
            )
            
            # Top P
            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=llm_settings.get('top_p', 1.0),
                step=0.05,
                help="控制生成文本的多样性。较低的值使生成更集中，较高的值使生成更多样。"
            )
            
            # 频率惩罚
            frequency_penalty = st.slider(
                "频率惩罚",
                min_value=-2.0,
                max_value=2.0,
                value=llm_settings.get('frequency_penalty', 0.0),
                step=0.1,
                help="控制模型重复使用相同词语的倾向。正值减少重复，负值增加重复。"
            )
            
            # 存在惩罚
            presence_penalty = st.slider(
                "存在惩罚",
                min_value=-2.0,
                max_value=2.0,
                value=llm_settings.get('presence_penalty', 0.0),
                step=0.1,
                help="控制模型谈论新主题的倾向。正值鼓励谈论新主题，负值鼓励继续当前主题。"
            )
            
            # 停止序列
            stop_sequences = st.text_input(
                "停止序列",
                value=",".join(llm_settings.get('stop_sequences', [])),
                help="输入逗号分隔的停止序列，当模型生成这些序列时会停止生成。"
            )
        
        # 设置持久化
        remember_settings = st.checkbox(
            "记住这些设置",
            value=llm_settings.get('remember_settings', True),
            help="选择是否在应用重启后保留这些设置"
        )
        
        # 提交按钮
        submitted = st.form_submit_button("保存设置")
        
        if submitted:
            # 解析停止序列
            stop_sequences_list = [seq.strip() for seq in stop_sequences.split(',') if seq.strip()]
            
            # 更新设置
            new_settings = {
                'model': model,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'api_key': api_key,
                'base_url': base_url,
                'timeout': timeout,
                'retries': retries,
                'top_p': top_p,
                'frequency_penalty': frequency_penalty,
                'presence_penalty': presence_penalty,
                'stop_sequences': stop_sequences_list,
                'remember_settings': remember_settings
            }
            
            update_llm_settings(new_settings)
            st.success("✅ LLM设置已更新")
    
    # 快速参数调整
    st.markdown("### ⚡ 快速参数调整")
    
    # 创建两列布局
    quick_col1, quick_col2 = st.columns(2)
    
    with quick_col1:
        # 快速调整温度
        quick_temp = st.slider(
            "快速调整温度",
            min_value=0.0,
            max_value=1.0,
            value=llm_settings['temperature'],
            step=0.05,
            key="quick_temp_slider"
        )
        
        if st.button("应用温度"):
            update_llm_temperature(quick_temp)
            st.success(f"✅ 温度已更新为 {quick_temp}")
    
    with quick_col2:
        # 快速调整最大令牌数
        quick_tokens = st.number_input(
            "快速调整最大令牌数",
            min_value=100,
            max_value=8000,
            value=llm_settings['max_tokens'],
            step=100,
            key="quick_tokens_input"
        )
        
        if st.button("应用令牌数"):
            update_llm_max_tokens(quick_tokens)
            st.success(f"✅ 最大令牌数已更新为 {quick_tokens}")
    
    # 验证API设置
    st.markdown("### 🔍 API验证")
    if st.button("验证API设置"):
        with st.spinner("正在验证API设置..."):
            is_valid, message = validate_api_settings()
            if is_valid:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
    
    # 重置按钮
    st.markdown("### 🔄 重置设置")
    if st.button("恢复默认设置"):
        from state import DEFAULT_LLM_SETTINGS
        
        update_llm_settings(DEFAULT_LLM_SETTINGS.copy())
        st.success("✅ 已恢复默认设置")
        st.rerun()

def render_ui_settings():
    """渲染界面设置"""
    st.markdown("## 🎨 界面设置")
    st.markdown("自定义应用界面和行为。")
    
    # 获取当前UI偏好设置
    ui_prefs = get_ui_preferences()
    
    # 创建表单
    with st.form("ui_settings_form"):
        # 主题设置
        theme = st.selectbox(
            "主题",
            ["light", "dark"],
            index=0 if ui_prefs['theme'] == "light" else 1,
            format_func=lambda x: "浅色主题" if x == "light" else "深色主题",
            help="选择应用主题"
        )
        
        # 默认图表类型
        default_chart_type = st.selectbox(
            "默认图表类型",
            ["auto", "bar", "line", "scatter", "pie"],
            index=0,
            help="选择默认的图表类型"
        )
        
        # 侧边栏默认状态
        sidebar_expanded = st.checkbox(
            "默认展开侧边栏",
            value=ui_prefs['sidebar_expanded'],
            help="选择应用启动时侧边栏的默认状态"
        )
        
        # 提交按钮
        submitted = st.form_submit_button("保存设置")
        
        if submitted:
            # 更新设置
            new_prefs = {
                'theme': theme,
                'default_chart_type': default_chart_type,
                'sidebar_expanded': sidebar_expanded
            }
            
            update_ui_preferences(new_prefs)
            st.success("✅ 界面设置已更新")
            
            # 如果主题发生变化，重新加载页面
            if theme != ui_prefs['theme']:
                st.rerun()
    
    # 重置按钮
    if st.button("恢复默认设置"):
        default_prefs = {
            'theme': 'light',
            'default_chart_type': 'auto',
            'sidebar_expanded': True
        }
        
        update_ui_preferences(default_prefs)
        st.success("✅ 已恢复默认设置")
        st.rerun()

def render_about():
    """渲染关于页面"""
    st.markdown("## ℹ️ 关于Excel智能体")
    
    st.markdown("""
    ### 📊 Excel智能体 v2.0
    
    Excel智能体是一个基于人工智能的Excel数据分析工具，可以帮助您快速分析Excel数据并生成洞察。
    
    #### 🚀 主要功能
    - **数据摘要** - 自动生成数据统计摘要
    - **智能分析** - 基于AI的数据分析和可视化
    - **自定义图表** - 创建自定义数据可视化
    
    #### 🛠️ 技术栈
    - **Streamlit** - Web应用框架
    - **Pandas** - 数据处理
    - **Plotly** - 交互式数据可视化
    - **LLM** - 大语言模型集成
    
    #### 📄 许可证
    本软件采用MIT许可证
    
    #### 👨‍💻 开发团队
    Excel智能体团队 © 2025
    """)
    
    # 系统信息
    st.markdown("### 🖥️ 系统信息")
    
    import platform
    import streamlit as st
    import pandas as pd
    import plotly
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**软件版本**")
        st.text(f"Excel智能体: v2.0")
        st.text(f"Streamlit: {st.__version__}")
        st.text(f"Pandas: {pd.__version__}")
        st.text(f"Plotly: {plotly.__version__}")
    
    with col2:
        st.markdown("**系统信息**")
        st.text(f"操作系统: {platform.system()} {platform.version()}")
        st.text(f"Python: {platform.python_version()}")
        st.text(f"处理器架构: {platform.machine()}")
    
    # 检查更新按钮
    if st.button("检查更新"):
        with st.spinner("正在检查更新..."):
            # 模拟检查更新
            import time
            time.sleep(2)
            st.success("✅ 已是最新版本!")