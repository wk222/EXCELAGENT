#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 主应用入口

模块化架构的主入口文件，负责初始化应用、设置页面配置和路由
"""

import streamlit as st
import os
import traceback
import sys
from state import initialize_state, get_ui_preferences, set_processing_state, log_action
from components.sidebar import render_sidebar
from components.widgets import error_card
from utils.styling import apply_global_styles
from components.feedback import success_notification, error_notification
from pages import home, analysis, custom_charts, settings
from utils.helpers import apply_theme, get_current_time_str

# 应用常量
APP_NAME = "Excel智能体"
APP_VERSION = "v2.0"
APP_ICON = "📊"
APP_SETTINGS_DIR = '.kiro/settings'

# 确保设置目录存在
os.makedirs(APP_SETTINGS_DIR, exist_ok=True)

def main():
    """主函数 - 应用入口点"""
    try:
        # 初始化应用
        initialize_app()
        
        # 渲染侧边栏并获取选中的页面
        selected_page = render_sidebar()
        
        # 使用错误边界包装页面渲染
        with error_boundary("页面渲染错误"):
            # 根据选中的页面渲染相应内容
            render_selected_page(selected_page)
        
        # 添加页脚
        render_footer()
        
        # 记录页面访问
        log_action(f"view_page_{selected_page}")
        
    except Exception as e:
        # 捕获全局异常
        handle_global_exception(e)

def initialize_app():
    """初始化应用环境和配置"""
    # 初始化应用状态
    initialize_state()
    
    # 获取UI偏好设置
    ui_prefs = get_ui_preferences()
    theme = ui_prefs.get('theme', 'light')
    sidebar_expanded = ui_prefs.get('sidebar_expanded', True)
    
    # 配置页面
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded" if sidebar_expanded else "collapsed",
        menu_items={
            'Get Help': 'https://github.com/excel-ai-agent/docs',
            'Report a bug': 'https://github.com/excel-ai-agent/issues',
            'About': f"{APP_NAME} {APP_VERSION} - 智能Excel数据分析助手"
        }
    )
    
    # 应用主题
    apply_theme(theme)
    
    # 应用全局样式
    apply_global_styles()
    
    # 记录应用启动
    log_action("app_initialized")

def render_selected_page(selected_page):
    """根据选择渲染对应页面"""
    # 页面路由映射
    page_routes = {
        "首页": home.render,
        "数据分析": analysis.render,
        "自定义图表": custom_charts.render,
        "设置": settings.render
    }
    
    # 获取对应的渲染函数
    render_func = page_routes.get(selected_page, home.render)
    
    # 执行渲染
    render_func()

def error_boundary(context="应用错误"):
    """错误边界上下文管理器"""
    class ErrorBoundary:
        def __init__(self, context):
            self.context = context
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                # 记录错误
                error_details = traceback.format_exc()
                log_action("error", {
                    "context": self.context,
                    "error_type": str(exc_type.__name__),
                    "error_message": str(exc_val)
                })
                
                # 显示错误通知
                error_notification(f"{self.context}: {str(exc_val)}")
                
                # 显示错误信息
                error_card(
                    f"{self.context}",
                    f"发生错误: {str(exc_val)}",
                    error_details
                )
                
                # 设置处理状态
                set_processing_state(False, str(exc_val))
                
                # 已处理异常
                return True
    
    return ErrorBoundary(context)

def handle_global_exception(exception):
    """处理全局未捕获的异常"""
    # 记录错误
    error_details = traceback.format_exc()
    log_action("global_error", {
        "error_type": str(type(exception).__name__),
        "error_message": str(exception)
    })
    
    # 显示错误通知
    error_notification("应用发生错误，请刷新页面或联系管理员")
    
    # 显示错误信息
    st.error("应用发生错误，请刷新页面或联系管理员")
    
    with st.expander("查看错误详情"):
        st.code(error_details)
    
    # 设置处理状态
    set_processing_state(False, str(exception))

def render_footer():
    """渲染页脚"""
    # 页脚HTML
    footer_html = f"""
    <div class="footer">
        <span>{APP_NAME} {APP_VERSION}</span>
        <span>|</span>
        <a href="#" onclick="document.getElementById('settings_btn').click(); return false;">设置</a>
        <span>|</span>
        <a href="#" onclick="document.getElementById('help_btn').click(); return false;">帮助</a>
        <span>|</span>
        <span>© 2025 Excel智能体团队</span>
    </div>
    
    <!-- 隐藏按钮 -->
    <div style="display: none;">
        <button id="settings_btn" onclick="window.location.href='#settings'">设置</button>
        <button id="help_btn">帮助</button>
    </div>
    """
    
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()