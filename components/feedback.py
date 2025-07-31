#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 视觉反馈组件

提供视觉反馈组件，如加载指示器、过渡动画和通知
"""

import streamlit as st
import time
import hashlib
from state import get_ui_preferences

def loading_spinner(text="处理中..."):
    """显示加载旋转器"""
    with st.spinner(text):
        yield

def loading_progress_bar(total_steps=100, key="progress"):
    """显示进度条加载指示器"""
    progress_bar = st.progress(0, text="准备中...")
    
    for i in range(total_steps + 1):
        # 更新进度条
        progress_bar.progress(i / total_steps, text=f"处理中... {i}%")
        
        # 模拟处理时间
        time.sleep(0.01)
    
    # 完成后清除进度条
    progress_bar.empty()

def loading_card(message="正在处理您的请求...", key="loading_card"):
    """显示加载卡片"""
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            st.markdown(f"""
            <div class="loading-card">
                <div class="loading-spinner"></div>
                <div class="loading-message">{message}</div>
            </div>
            
            <style>
            .loading-card {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: var(--spacing-lg);
                background-color: var(--color-surface);
                border-radius: var(--border-radius-md);
                border: 1px solid var(--color-border);
                box-shadow: var(--shadow-md);
                margin: var(--spacing-lg) 0;
            }}
            
            .loading-spinner {{
                width: 40px;
                height: 40px;
                border: 4px solid rgba(0, 0, 0, 0.1);
                border-left-color: var(--color-primary);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: var(--spacing-md);
            }}
            
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
            
            .loading-message {{
                color: var(--color-text);
                font-weight: var(--font-weight-medium);
                text-align: center;
            }}
            </style>
            """, unsafe_allow_html=True)

def success_notification(message, duration=3):
    """显示成功通知"""
    notification_id = "success_notification"
    
    # 创建通知HTML
    notification_html = f"""
    <div id="{notification_id}" class="notification success-notification">
        <div class="notification-icon">✓</div>
        <div class="notification-content">{message}</div>
    </div>
    
    <style>
    .notification {{
        position: fixed;
        top: 20px;
        right: 20px;
        display: flex;
        align-items: center;
        padding: var(--spacing-md);
        border-radius: var(--border-radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 9999;
        animation: slideIn 0.3s ease-out, fadeOut 0.5s ease-in {duration}s forwards;
        max-width: 300px;
    }}
    
    .success-notification {{
        background-color: var(--color-success);
        color: white;
    }}
    
    .notification-icon {{
        font-size: 1.2rem;
        margin-right: var(--spacing-sm);
    }}
    
    .notification-content {{
        font-weight: var(--font-weight-medium);
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateX(100%); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    @keyframes fadeOut {{
        from {{ opacity: 1; }}
        to {{ opacity: 0; visibility: hidden; }}
    }}
    </style>
    """
    
    # 显示通知
    st.markdown(notification_html, unsafe_allow_html=True)

def error_notification(message, duration=5):
    """显示错误通知"""
    notification_id = "error_notification"
    
    # 创建通知HTML
    notification_html = f"""
    <div id="{notification_id}" class="notification error-notification">
        <div class="notification-icon">✗</div>
        <div class="notification-content">{message}</div>
    </div>
    
    <style>
    .notification {{
        position: fixed;
        top: 20px;
        right: 20px;
        display: flex;
        align-items: center;
        padding: var(--spacing-md);
        border-radius: var(--border-radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 9999;
        animation: slideIn 0.3s ease-out, fadeOut 0.5s ease-in {duration}s forwards;
        max-width: 300px;
    }}
    
    .error-notification {{
        background-color: var(--color-danger);
        color: white;
    }}
    
    .notification-icon {{
        font-size: 1.2rem;
        margin-right: var(--spacing-sm);
    }}
    
    .notification-content {{
        font-weight: var(--font-weight-medium);
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateX(100%); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    @keyframes fadeOut {{
        from {{ opacity: 1; }}
        to {{ opacity: 0; visibility: hidden; }}
    }}
    </style>
    """
    
    # 显示通知
    st.markdown(notification_html, unsafe_allow_html=True)

def info_notification(message, duration=4):
    """显示信息通知"""
    notification_id = "info_notification"
    
    # 创建通知HTML
    notification_html = f"""
    <div id="{notification_id}" class="notification info-notification">
        <div class="notification-icon">ℹ</div>
        <div class="notification-content">{message}</div>
    </div>
    
    <style>
    .notification {{
        position: fixed;
        top: 20px;
        right: 20px;
        display: flex;
        align-items: center;
        padding: var(--spacing-md);
        border-radius: var(--border-radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 9999;
        animation: slideIn 0.3s ease-out, fadeOut 0.5s ease-in {duration}s forwards;
        max-width: 300px;
    }}
    
    .info-notification {{
        background-color: var(--color-info);
        color: white;
    }}
    
    .notification-icon {{
        font-size: 1.2rem;
        margin-right: var(--spacing-sm);
    }}
    
    .notification-content {{
        font-weight: var(--font-weight-medium);
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateX(100%); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    @keyframes fadeOut {{
        from {{ opacity: 1; }}
        to {{ opacity: 0; visibility: hidden; }}
    }}
    </style>
    """
    
    # 显示通知
    st.markdown(notification_html, unsafe_allow_html=True)

def animated_container(content_func, animation_type="fade-in", key=None):
    """创建带有动画效果的容器"""
    
    # 生成更稳定的container_id
    if key:
        container_id = f"animated_container_{key}"
    else:
        # 使用函数名和animation_type生成稳定的hash
        func_name = getattr(content_func, '__name__', 'anonymous')
        hash_input = f"{func_name}_{animation_type}"
        container_id = f"animated_container_{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"
    
    # 开始动画容器
    st.markdown(f'<div id="{container_id}" class="{animation_type}">', unsafe_allow_html=True)
    
    # 执行内容函数
    content_func()
    
    # 结束动画容器
    st.markdown('</div>', unsafe_allow_html=True)

def button_with_loading(label, on_click=None, key=None, help=None, args=None, kwargs=None):
    """带有加载状态的按钮"""
    # 初始化按钮状态
    if f"{key}_loading" not in st.session_state:
        st.session_state[f"{key}_loading"] = False
    
    # 如果按钮正在加载中，显示加载状态
    if st.session_state[f"{key}_loading"]:
        st.button(
            f"处理中...",
            key=f"{key}_disabled",
            disabled=True,
            help=help
        )
        return False
    
    # 否则显示正常按钮
    clicked = st.button(label, key=key, help=help)
    
    # 如果按钮被点击
    if clicked and on_click:
        # 设置加载状态
        st.session_state[f"{key}_loading"] = True
        
        try:
            # 执行回调函数
            if args and kwargs:
                on_click(*args, **kwargs)
            elif args:
                on_click(*args)
            elif kwargs:
                on_click(**kwargs)
            else:
                on_click()
        finally:
            # 重置加载状态
            st.session_state[f"{key}_loading"] = False
        
        # 重新运行应用以更新UI
        st.rerun()
    
    return clicked

def transition_effect(element_id, effect="fade-in"):
    """为元素添加过渡效果"""
    effects = {
        "fade-in": "opacity: 0; animation: fadeIn 0.5s forwards;",
        "slide-in": "transform: translateY(20px); opacity: 0; animation: slideIn 0.5s forwards;",
        "slide-in-left": "transform: translateX(-20px); opacity: 0; animation: slideInLeft 0.5s forwards;",
        "slide-in-right": "transform: translateX(20px); opacity: 0; animation: slideInRight 0.5s forwards;",
        "zoom-in": "transform: scale(0.9); opacity: 0; animation: zoomIn 0.5s forwards;",
        "bounce-in": "transform: scale(0.3); opacity: 0; animation: bounceIn 0.5s cubic-bezier(0.215, 0.610, 0.355, 1.000) forwards;"
    }
    
    effect_css = effects.get(effect, effects["fade-in"])
    
    # 添加CSS动画
    st.markdown(f"""
    <style>
    #{element_id} {{
        {effect_css}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateY(20px); opacity: 0; }}
        to {{ transform: translateY(0); opacity: 1; }}
    }}
    
    @keyframes slideInLeft {{
        from {{ transform: translateX(-20px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    @keyframes slideInRight {{
        from {{ transform: translateX(20px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    @keyframes zoomIn {{
        from {{ transform: scale(0.9); opacity: 0; }}
        to {{ transform: scale(1); opacity: 1; }}
    }}
    
    @keyframes bounceIn {{
        0% {{ transform: scale(0.3); opacity: 0; }}
        20% {{ transform: scale(1.1); }}
        40% {{ transform: scale(0.9); }}
        60% {{ transform: scale(1.03); }}
        80% {{ transform: scale(0.97); }}
        100% {{ transform: scale(1); opacity: 1; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def pulse_effect(element_id):
    """为元素添加脉冲效果"""
    st.markdown(f"""
    <style>
    #{element_id} {{
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def highlight_effect(element_id, duration=2):
    """为元素添加高亮效果"""
    st.markdown(f"""
    <style>
    #{element_id} {{
        animation: highlight {duration}s;
    }}
    
    @keyframes highlight {{
        0% {{ background-color: transparent; }}
        30% {{ background-color: var(--color-focus); }}
        100% {{ background-color: transparent; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def shake_effect(element_id):
    """为元素添加摇晃效果（用于错误提示）"""
    st.markdown(f"""
    <style>
    #{element_id} {{
        animation: shake 0.5s;
    }}
    
    @keyframes shake {{
        0%, 100% {{ transform: translateX(0); }}
        10%, 30%, 50%, 70%, 90% {{ transform: translateX(-5px); }}
        20%, 40%, 60%, 80% {{ transform: translateX(5px); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def add_loading_overlay():
    """添加全屏加载覆盖层"""
    st.markdown("""
    <div class="loading-overlay">
        <div class="loading-spinner-large"></div>
        <div class="loading-text">处理中，请稍候...</div>
    </div>
    
    <style>
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .loading-spinner-large {
        width: 60px;
        height: 60px;
        border: 6px solid rgba(255, 255, 255, 0.3);
        border-left-color: white;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .loading-text {
        color: white;
        font-size: 1.2rem;
        margin-top: 20px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

def remove_loading_overlay():
    """移除全屏加载覆盖层"""
    st.markdown("""
    <style>
    .loading-overlay {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

def add_tooltip(element_id, tooltip_text):
    """为元素添加工具提示"""
    st.markdown(f"""
    <style>
    #{element_id} {{
        position: relative;
    }}
    
    #{element_id}:hover::after {{
        content: "{tooltip_text}";
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background-color: var(--color-surface);
        color: var(--color-text);
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--border-radius-sm);
        border: 1px solid var(--color-border);
        font-size: 0.8rem;
        white-space: nowrap;
        z-index: 1000;
        box-shadow: var(--shadow-md);
    }}
    </style>
    """, unsafe_allow_html=True)