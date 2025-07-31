#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 侧边栏组件

负责渲染应用的侧边栏导航和快速设置
"""

import streamlit as st
from state import get_ui_preferences, update_ui_preferences, get_llm_settings, update_llm_settings

def render_sidebar():
    """渲染侧边栏并返回选中的页面"""
    with st.sidebar:
        # 应用自定义CSS
        apply_sidebar_css()
        
        # 侧边栏标题
        st.markdown('<div class="sidebar-header">📊 Excel智能体</div>', unsafe_allow_html=True)
        
        # 导航菜单
        st.markdown('<div class="nav-section-header">导航</div>', unsafe_allow_html=True)
        
        # 导航选项
        nav_options = {
            "首页": {"icon": "🏠", "desc": "欢迎页面和文件上传"},
            "数据分析": {"icon": "📊", "desc": "多阶段数据分析"},
            "自定义图表": {"icon": "📈", "desc": "创建自定义可视化"},
            "设置": {"icon": "⚙️", "desc": "应用设置和参数配置"}
        }
        
        # 获取当前选中的页面
        if 'sidebar_selection' not in st.session_state:
            st.session_state.sidebar_selection = "首页"
        
        # 渲染导航按钮
        for page, info in nav_options.items():
            is_selected = st.session_state.sidebar_selection == page
            button_class = "nav-button selected" if is_selected else "nav-button"
            
            # 创建自定义按钮
            button_html = f"""
            <div class="{button_class}" id="nav-{page}">
                <div class="nav-icon">{info['icon']}</div>
                <div class="nav-content">
                    <div class="nav-title">{page}</div>
                    <div class="nav-desc">{info['desc']}</div>
                </div>
            </div>
            """
            
            # 使用空白容器和点击事件
            nav_container = st.container()
            nav_container.markdown(button_html, unsafe_allow_html=True)
            
            # 使用按钮作为点击触发器（隐藏样式）
            if nav_container.button(f"选择{page}", key=f"nav_{page}", help=info['desc'], use_container_width=True):
                st.session_state.sidebar_selection = page
                st.rerun()
        
        st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
        
        # 快速设置
        st.markdown('<div class="nav-section-header">LLM快速设置</div>', unsafe_allow_html=True)
        
        # 获取当前LLM设置
        llm_settings = get_llm_settings()
        
        # 温度参数
        temp_col1, temp_col2 = st.columns([3, 1])
        with temp_col1:
            new_temp = st.slider(
                "温度系数",
                min_value=0.0,
                max_value=1.0,
                value=llm_settings['temperature'],
                step=0.1,
                key="sidebar_temperature",
                help="控制AI生成结果的创造性"
            )
        with temp_col2:
            st.markdown(f"<div class='param-value'>{new_temp:.1f}</div>", unsafe_allow_html=True)
        
        # 如果值发生变化，更新设置
        if new_temp != llm_settings['temperature']:
            update_llm_settings({'temperature': new_temp})
        
        # 最大令牌数
        tokens_col1, tokens_col2 = st.columns([3, 1])
        with tokens_col1:
            new_tokens = st.select_slider(
                "最大令牌数",
                options=[500, 1000, 1500, 2000, 3000, 4000, 6000, 8000],
                value=llm_settings['max_tokens'],
                key="sidebar_max_tokens",
                help="控制生成文本的最大长度"
            )
        with tokens_col2:
            st.markdown(f"<div class='param-value'>{new_tokens}</div>", unsafe_allow_html=True)
        
        # 如果值发生变化，更新设置
        if new_tokens != llm_settings['max_tokens']:
            update_llm_settings({'max_tokens': new_tokens})
        
        # 模型选择
        from logic.llm_service import get_available_models
        available_models = get_available_models()
        
        # 确保当前模型在列表中
        if llm_settings['model'] not in available_models:
            available_models.append(llm_settings['model'])
        
        model_index = available_models.index(llm_settings['model']) if llm_settings['model'] in available_models else 0
        
        # 使用下拉菜单选择模型
        new_model = st.selectbox(
            "模型",
            available_models,
            index=model_index,
            key="sidebar_model",
            help="选择要使用的大语言模型"
        )
        
        # 如果值发生变化，更新设置
        if new_model != llm_settings['model']:
            update_llm_settings({'model': new_model})
        
        # 主题切换
        ui_prefs = get_ui_preferences()
        theme = ui_prefs.get('theme', 'light')
        
        theme_col1, theme_col2 = st.columns([1, 1])
        with theme_col1:
            st.markdown("<div class='setting-label'>主题</div>", unsafe_allow_html=True)
        with theme_col2:
            # 使用自定义切换按钮
            is_dark = theme == "dark"
            theme_toggle_html = f"""
            <div class="theme-toggle-container">
                <div class="theme-icon">☀️</div>
                <div class="theme-toggle {is_dark and 'active' or ''}"></div>
                <div class="theme-icon">🌙</div>
            </div>
            """
            st.markdown(theme_toggle_html, unsafe_allow_html=True)
            
            # 使用隐藏按钮作为切换触发器
            if st.button("切换主题", key="theme_toggle", help="切换浅色/深色主题"):
                new_theme = "dark" if theme == "light" else "light"
                update_ui_preferences({'theme': new_theme})
                st.rerun()
        
        # 文件状态
        if st.session_state.uploaded_file_data is not None:
            st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
            st.markdown('<div class="nav-section-header">当前文件</div>', unsafe_allow_html=True)
            
            file_data = st.session_state.uploaded_file_data
            file_info_html = f"""
            <div class="file-info">
                <div class="file-name">{file_data['filename']}</div>
                <div class="file-details">
                    <span class="file-sheet">{file_data['current_sheet']}</span> | 
                    <span class="file-size">{file_data['shape'][0]} 行 × {file_data['shape'][1]} 列</span>
                </div>
            </div>
            """
            st.markdown(file_info_html, unsafe_allow_html=True)
            
            # 清除文件按钮
            if st.button("清除文件", key="clear_file", help="清除当前加载的文件"):
                st.session_state.uploaded_file_data = None
                from state import reset_all_stages
                reset_all_stages()
        
        # 应用信息
        st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
        st.markdown('<div class="app-info">Excel智能体 v2.0</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-copyright">© 2025 Excel智能体团队</div>', unsafe_allow_html=True)
    
    return st.session_state.sidebar_selection

def apply_sidebar_css():
    """应用侧边栏自定义CSS"""
    # 使用新的样式系统
    from utils.styling import apply_component_styles
    apply_component_styles("sidebar")