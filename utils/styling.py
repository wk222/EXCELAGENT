#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 样式系统

定义应用的样式系统，包括颜色方案、排版、间距和布局指南
"""

import streamlit as st
from state import get_ui_preferences

# 颜色方案
COLOR_SCHEMES = {
    "light": {
        "primary": "#1f77b4",        # 主色调 - 蓝色
        "secondary": "#ff7f0e",      # 次要色调 - 橙色
        "success": "#28a745",        # 成功色调 - 绿色
        "warning": "#ffc107",        # 警告色调 - 黄色
        "danger": "#dc3545",         # 危险色调 - 红色
        "info": "#17a2b8",           # 信息色调 - 青色
        "background": "#f8f9fa",     # 背景色 - 浅灰
        "surface": "#ffffff",        # 表面色 - 白色
        "text": "#333333",           # 文本色 - 深灰
        "text_secondary": "#6c757d", # 次要文本色 - 中灰
        "border": "#e9ecef",         # 边框色 - 浅灰
        "hover": "#e2e6ea",          # 悬停色 - 浅灰
        "focus": "#d1ecf1",          # 焦点色 - 浅青
        "disabled": "#f8f9fa",       # 禁用色 - 浅灰
        "shadow": "rgba(0,0,0,0.05)" # 阴影色 - 半透明黑
    },
    "dark": {
        "primary": "#4da6ff",        # 主色调 - 亮蓝
        "secondary": "#ff9e45",      # 次要色调 - 亮橙
        "success": "#5cb85c",        # 成功色调 - 亮绿
        "warning": "#f0ad4e",        # 警告色调 - 亮黄
        "danger": "#d9534f",         # 危险色调 - 亮红
        "info": "#5bc0de",           # 信息色调 - 亮青
        "background": "#0e1117",     # 背景色 - 深灰
        "surface": "#262730",        # 表面色 - 中灰
        "text": "#ffffff",           # 文本色 - 白色
        "text_secondary": "#adb5bd", # 次要文本色 - 浅灰
        "border": "#4a4b56",         # 边框色 - 中灰
        "hover": "#3a3b47",          # 悬停色 - 中灰
        "focus": "#3a4a54",          # 焦点色 - 深青
        "disabled": "#3a3b47",       # 禁用色 - 中灰
        "shadow": "rgba(0,0,0,0.2)"  # 阴影色 - 半透明黑
    }
}

# 排版定义
TYPOGRAPHY = {
    "font_family": "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif",
    "heading_sizes": {
        "h1": "2.5rem",
        "h2": "2rem",
        "h3": "1.75rem",
        "h4": "1.5rem",
        "h5": "1.25rem",
        "h6": "1rem"
    },
    "font_weights": {
        "light": 300,
        "regular": 400,
        "medium": 500,
        "bold": 700
    },
    "line_heights": {
        "tight": 1.2,
        "normal": 1.5,
        "loose": 1.8
    }
}

# 间距系统
SPACING = {
    "xs": "0.25rem",   # 4px
    "sm": "0.5rem",    # 8px
    "md": "1rem",      # 16px
    "lg": "1.5rem",    # 24px
    "xl": "2rem",      # 32px
    "xxl": "3rem"      # 48px
}

# 边框圆角
BORDER_RADIUS = {
    "sm": "0.25rem",   # 4px
    "md": "0.5rem",    # 8px
    "lg": "1rem",      # 16px
    "pill": "50rem"    # 圆形按钮
}

# 阴影定义
SHADOWS = {
    "sm": "0 1px 2px {shadow}",
    "md": "0 2px 5px {shadow}",
    "lg": "0 5px 15px {shadow}",
    "xl": "0 10px 25px {shadow}"
}

# 动画定义
ANIMATIONS = {
    "transition_fast": "0.15s ease-in-out",
    "transition_normal": "0.3s ease-in-out",
    "transition_slow": "0.5s ease-in-out"
}

# 布局断点
BREAKPOINTS = {
    "xs": "0px",       # 超小屏幕
    "sm": "576px",     # 小屏幕
    "md": "768px",     # 中等屏幕
    "lg": "992px",     # 大屏幕
    "xl": "1200px"     # 超大屏幕
}

# 获取当前主题的颜色方案
def get_color_scheme():
    """获取当前主题的颜色方案"""
    ui_prefs = get_ui_preferences()
    theme = ui_prefs.get('theme', 'light')
    return COLOR_SCHEMES[theme]

# 生成CSS变量
def generate_css_variables():
    """生成CSS变量"""
    ui_prefs = get_ui_preferences()
    theme = ui_prefs.get('theme', 'light')
    colors = COLOR_SCHEMES[theme]
    
    css_vars = []
    
    # 颜色变量
    for name, value in colors.items():
        css_vars.append(f"--color-{name}: {value};")
    
    # 排版变量
    css_vars.append(f"--font-family: {TYPOGRAPHY['font_family']};")
    for name, size in TYPOGRAPHY['heading_sizes'].items():
        css_vars.append(f"--font-size-{name}: {size};")
    for name, weight in TYPOGRAPHY['font_weights'].items():
        css_vars.append(f"--font-weight-{name}: {weight};")
    for name, height in TYPOGRAPHY['line_heights'].items():
        css_vars.append(f"--line-height-{name}: {height};")
    
    # 间距变量
    for name, value in SPACING.items():
        css_vars.append(f"--spacing-{name}: {value};")
    
    # 边框圆角变量
    for name, value in BORDER_RADIUS.items():
        css_vars.append(f"--border-radius-{name}: {value};")
    
    # 阴影变量
    for name, value in SHADOWS.items():
        shadow_value = value.format(shadow=colors["shadow"])
        css_vars.append(f"--shadow-{name}: {shadow_value};")
    
    # 动画变量
    for name, value in ANIMATIONS.items():
        css_vars.append(f"--{name}: {value};")
    
    # 断点变量
    for name, value in BREAKPOINTS.items():
        css_vars.append(f"--breakpoint-{name}: {value};")
    
    return "\n    ".join(css_vars)

# 应用全局样式
def apply_global_styles():
    """应用全局样式"""
    css_variables = generate_css_variables()
    colors = get_color_scheme()
    
    # 全局CSS
    st.markdown(f"""
    <style>
    :root {{
    {css_variables}
    }}
    
    /* 全局样式 */
    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }}
    
    .stApp {{
        background-color: var(--color-background);
        color: var(--color-text);
        font-family: var(--font-family);
        line-height: var(--line-height-normal);
    }}
    
    /* 排版样式 */
    h1, .h1 {{
        font-size: var(--font-size-h1);
        font-weight: var(--font-weight-bold);
        line-height: var(--line-height-tight);
        color: var(--color-primary);
        margin-bottom: var(--spacing-lg);
    }}
    
    h2, .h2 {{
        font-size: var(--font-size-h2);
        font-weight: var(--font-weight-bold);
        line-height: var(--line-height-tight);
        color: var(--color-primary);
        margin-bottom: var(--spacing-md);
    }}
    
    h3, .h3 {{
        font-size: var(--font-size-h3);
        font-weight: var(--font-weight-medium);
        line-height: var(--line-height-tight);
        color: var(--color-primary);
        margin-bottom: var(--spacing-md);
    }}
    
    h4, .h4 {{
        font-size: var(--font-size-h4);
        font-weight: var(--font-weight-medium);
        line-height: var(--line-height-tight);
        color: var(--color-primary);
        margin-bottom: var(--spacing-sm);
    }}
    
    h5, .h5 {{
        font-size: var(--font-size-h5);
        font-weight: var(--font-weight-medium);
        line-height: var(--line-height-tight);
        color: var(--color-primary);
        margin-bottom: var(--spacing-sm);
    }}
    
    h6, .h6 {{
        font-size: var(--font-size-h6);
        font-weight: var(--font-weight-medium);
        line-height: var(--line-height-tight);
        color: var(--color-primary);
        margin-bottom: var(--spacing-sm);
    }}
    
    p {{
        margin-bottom: var(--spacing-md);
    }}
    
    a {{
        color: var(--color-primary);
        text-decoration: none;
        transition: color var(--transition-fast);
    }}
    
    a:hover {{
        text-decoration: underline;
    }}
    
    /* 卡片样式 */
    .card {{
        background-color: var(--color-surface);
        border-radius: var(--border-radius-md);
        padding: var(--spacing-lg);
        margin-bottom: var(--spacing-lg);
        border: 1px solid var(--color-border);
        box-shadow: var(--shadow-md);
    }}
    
    .card-header {{
        font-size: var(--font-size-h5);
        font-weight: var(--font-weight-medium);
        color: var(--color-primary);
        margin-bottom: var(--spacing-md);
        padding-bottom: var(--spacing-sm);
        border-bottom: 1px solid var(--color-border);
    }}
    
    .card-footer {{
        margin-top: var(--spacing-md);
        padding-top: var(--spacing-sm);
        border-top: 1px solid var(--color-border);
        text-align: right;
    }}
    
    /* 按钮样式 */
    .stButton>button {{
        background-color: var(--color-primary);
        color: white;
        border: none;
        border-radius: var(--border-radius-md);
        padding: var(--spacing-sm) var(--spacing-md);
        font-weight: var(--font-weight-medium);
        transition: background-color var(--transition-fast);
    }}
    
    .stButton>button:hover {{
        background-color: var(--color-primary);
        filter: brightness(90%);
    }}
    
    /* 输入框样式 */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input {{
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-md);
        padding: var(--spacing-sm);
        transition: border-color var(--transition-fast);
    }}
    
    .stTextInput>div>div>input:focus, 
    .stNumberInput>div>div>input:focus {{
        border-color: var(--color-primary);
        box-shadow: 0 0 0 2px var(--color-focus);
    }}
    
    /* 选择框样式 */
    .stSelectbox>div>div>div {{
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-md);
    }}
    
    /* 滑块样式 */
    .stSlider>div>div>div>div>div {{
        background-color: var(--color-primary);
    }}
    
    /* 表格样式 */
    .stDataFrame {{
        border: 1px solid var(--color-border);
    }}
    
    .stDataFrame th {{
        background-color: var(--color-background);
        color: var(--color-text);
        font-weight: var(--font-weight-medium);
    }}
    
    /* 阶段卡片样式 */
    .stage-card {{
        border-left: 4px solid var(--color-primary);
    }}
    
    .stage-pending {{
        border-left-color: var(--color-warning);
    }}
    
    .stage-in-progress {{
        border-left-color: var(--color-info);
    }}
    
    .stage-completed {{
        border-left-color: var(--color-success);
    }}
    
    .stage-error {{
        border-left-color: var(--color-danger);
    }}
    
    /* 状态徽章样式 */
    .status-badge {{
        display: inline-block;
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--border-radius-sm);
        font-size: 0.8rem;
        font-weight: var(--font-weight-medium);
    }}
    
    .status-pending {{
        background-color: #fff3cd;
        color: #856404;
    }}
    
    .status-in-progress {{
        background-color: #d1ecf1;
        color: #0c5460;
    }}
    
    .status-completed {{
        background-color: #d4edda;
        color: #155724;
    }}
    
    .status-error {{
        background-color: #f8d7da;
        color: #721c24;
    }}
    
    /* 指标卡片样式 */
    .metric-card {{
        background-color: var(--color-surface);
        border-radius: var(--border-radius-md);
        padding: var(--spacing-md);
        text-align: center;
        border: 1px solid var(--color-border);
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: var(--font-weight-bold);
        color: var(--color-primary);
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: var(--color-text-secondary);
    }}
    
    /* 图表容器样式 */
    .chart-container {{
        background-color: var(--color-surface);
        border-radius: var(--border-radius-md);
        padding: var(--spacing-md);
        border: 1px solid var(--color-border);
        margin-bottom: var(--spacing-md);
    }}
    
    .chart-title {{
        font-size: 1.1rem;
        font-weight: var(--font-weight-medium);
        color: var(--color-primary);
        margin-bottom: var(--spacing-sm);
    }}
    
    .chart-description {{
        font-size: 0.9rem;
        color: var(--color-text-secondary);
        margin-bottom: var(--spacing-md);
    }}
    
    /* 文件信息卡片样式 */
    .file-info-card {{
        background-color: var(--color-surface);
        border-radius: var(--border-radius-md);
        padding: var(--spacing-md);
        border: 1px solid var(--color-border);
        margin-bottom: var(--spacing-md);
    }}
    
    .file-name {{
        font-size: 1.1rem;
        font-weight: var(--font-weight-medium);
        color: var(--color-primary);
    }}
    
    .file-details {{
        font-size: 0.9rem;
        color: var(--color-text-secondary);
    }}
    
    /* 代码块样式 */
    .code-block {{
        border-radius: var(--border-radius-md);
        border: 1px solid var(--color-border);
        margin-bottom: var(--spacing-md);
    }}
    
    .code-header {{
        background-color: var(--color-surface);
        padding: var(--spacing-sm) var(--spacing-md);
        border-bottom: 1px solid var(--color-border);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .code-title {{
        font-weight: var(--font-weight-medium);
        color: var(--color-primary);
    }}
    
    .code-actions {{
        display: flex;
        gap: var(--spacing-sm);
    }}
    
    .code-action-button {{
        background-color: transparent;
        border: none;
        color: var(--color-text);
        cursor: pointer;
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--border-radius-sm);
        transition: background-color var(--transition-fast);
    }}
    
    .code-action-button:hover {{
        background-color: var(--color-hover);
    }}
    
    /* 进度步骤样式 */
    .steps-container {{
        display: flex;
        justify-content: space-between;
        margin: var(--spacing-md) 0 var(--spacing-lg) 0;
        position: relative;
    }}
    
    .steps-container:before {{
        content: '';
        position: absolute;
        top: 15px;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--color-border);
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
        background-color: var(--color-border);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto var(--spacing-sm) auto;
        font-weight: var(--font-weight-bold);
        color: white;
    }}
    
    .step-active .step-circle {{
        background-color: var(--color-primary);
    }}
    
    .step-completed .step-circle {{
        background-color: var(--color-success);
    }}
    
    .step-label {{
        font-size: 0.8rem;
        color: var(--color-text);
        max-width: 100px;
        margin: 0 auto;
    }}
    
    .step-active .step-label {{
        font-weight: var(--font-weight-medium);
        color: var(--color-primary);
    }}
    
    /* 自定义标签页样式 */
    .custom-tabs {{
        display: flex;
        border-bottom: 1px solid var(--color-border);
        margin-bottom: var(--spacing-md);
    }}
    
    .custom-tab {{
        padding: var(--spacing-sm) var(--spacing-lg);
        cursor: pointer;
        border: 1px solid transparent;
        border-bottom: none;
        border-radius: var(--border-radius-sm) var(--border-radius-sm) 0 0;
        margin-right: var(--spacing-xs);
        font-weight: var(--font-weight-medium);
        transition: all var(--transition-fast);
    }}
    
    .custom-tab-active {{
        background-color: var(--color-surface);
        color: var(--color-primary);
        border-color: var(--color-border);
        border-bottom: 2px solid var(--color-surface);
        margin-bottom: -1px;
    }}
    
    .custom-tab-inactive {{
        background-color: var(--color-background);
        color: var(--color-text-secondary);
    }}
    
    .custom-tab-inactive:hover {{
        background-color: var(--color-hover);
        color: var(--color-primary);
    }}
    
    /* 响应式布局辅助类 */
    .hide-on-mobile {{
        display: block;
    }}
    
    @media (max-width: 768px) {{
        .hide-on-mobile {{
            display: none;
        }}
    }}
    
    /* 动画效果 */
    .fade-in {{
        animation: fadeIn var(--transition-normal);
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    .slide-in {{
        animation: slideIn var(--transition-normal);
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateY(20px); opacity: 0; }}
        to {{ transform: translateY(0); opacity: 1; }}
    }}
    
    /* 页脚样式 */
    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 30px;
        background-color: var(--color-background);
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 0.8rem;
        color: var(--color-text-secondary);
        border-top: 1px solid var(--color-border);
        z-index: 100;
    }}
    
    .footer a {{
        color: var(--color-primary);
        text-decoration: none;
        margin: 0 var(--spacing-sm);
    }}
    
    .footer a:hover {{
        text-decoration: underline;
    }}
    
    /* 为页脚腾出空间 */
    .main .block-container {{
        padding-bottom: 50px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 应用组件特定样式
def apply_component_styles(component_name):
    """应用组件特定样式"""
    if component_name == "sidebar":
        st.markdown("""
        <style>
        .sidebar-header {
            font-size: var(--font-size-h4);
            font-weight: var(--font-weight-bold);
            color: var(--color-primary);
            margin-bottom: var(--spacing-md);
            padding-bottom: var(--spacing-sm);
            border-bottom: 1px solid var(--color-border);
        }
        
        .sidebar-section {
            margin-bottom: var(--spacing-lg);
        }
        
        .sidebar-section-title {
            font-size: var(--font-size-h6);
            font-weight: var(--font-weight-medium);
            color: var(--color-text-secondary);
            margin-bottom: var(--spacing-sm);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .sidebar-nav-item {
            display: flex;
            align-items: center;
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: var(--border-radius-md);
            margin-bottom: var(--spacing-xs);
            transition: background-color var(--transition-fast);
            cursor: pointer;
        }
        
        .sidebar-nav-item:hover {
            background-color: var(--color-hover);
        }
        
        .sidebar-nav-item.active {
            background-color: var(--color-primary);
            color: white;
        }
        
        .sidebar-nav-icon {
            margin-right: var(--spacing-sm);
            width: 20px;
            text-align: center;
        }
        
        .sidebar-footer {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: var(--spacing-md);
            font-size: 0.8rem;
            color: var(--color-text-secondary);
            border-top: 1px solid var(--color-border);
        }
        </style>
        """, unsafe_allow_html=True)
    
    elif component_name == "file_uploader":
        st.markdown("""
        <style>
        .file-upload-area {
            border: 2px dashed var(--color-border);
            border-radius: var(--border-radius-md);
            padding: var(--spacing-lg);
            text-align: center;
            transition: border-color var(--transition-fast);
            cursor: pointer;
        }
        
        .file-upload-area:hover {
            border-color: var(--color-primary);
        }
        
        .file-upload-icon {
            font-size: 2rem;
            color: var(--color-primary);
            margin-bottom: var(--spacing-sm);
        }
        
        .file-upload-text {
            color: var(--color-text-secondary);
            margin-bottom: var(--spacing-md);
        }
        
        .file-upload-button {
            background-color: var(--color-primary);
            color: white;
            border: none;
            border-radius: var(--border-radius-md);
            padding: var(--spacing-sm) var(--spacing-md);
            font-weight: var(--font-weight-medium);
            cursor: pointer;
            transition: background-color var(--transition-fast);
        }
        
        .file-upload-button:hover {
            background-color: var(--color-primary);
            filter: brightness(90%);
        }
        </style>
        """, unsafe_allow_html=True)
    
    elif component_name == "analysis_stages":
        st.markdown("""
        <style>
        .analysis-stage {
            margin-bottom: var(--spacing-lg);
        }
        
        .analysis-stage-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--spacing-sm);
        }
        
        .analysis-stage-title {
            font-size: var(--font-size-h5);
            font-weight: var(--font-weight-medium);
            color: var(--color-primary);
        }
        
        .analysis-stage-status {
            font-size: 0.8rem;
        }
        
        .analysis-stage-content {
            background-color: var(--color-surface);
            border-radius: var(--border-radius-md);
            padding: var(--spacing-md);
            border: 1px solid var(--color-border);
        }
        
        .analysis-stage-actions {
            margin-top: var(--spacing-md);
            display: flex;
            justify-content: flex-end;
            gap: var(--spacing-sm);
        }
        </style>
        """, unsafe_allow_html=True)
    
    elif component_name == "settings_page":
        st.markdown("""
        <style>
        .settings-section {
            margin-bottom: var(--spacing-xl);
        }
        
        .settings-section-title {
            font-size: var(--font-size-h4);
            font-weight: var(--font-weight-medium);
            color: var(--color-primary);
            margin-bottom: var(--spacing-md);
            padding-bottom: var(--spacing-sm);
            border-bottom: 1px solid var(--color-border);
        }
        
        .settings-group {
            background-color: var(--color-surface);
            border-radius: var(--border-radius-md);
            padding: var(--spacing-lg);
            border: 1px solid var(--color-border);
            margin-bottom: var(--spacing-lg);
        }
        
        .settings-group-title {
            font-size: var(--font-size-h5);
            font-weight: var(--font-weight-medium);
            color: var(--color-primary);
            margin-bottom: var(--spacing-md);
        }
        
        .settings-item {
            margin-bottom: var(--spacing-md);
        }
        
        .settings-label {
            font-weight: var(--font-weight-medium);
            margin-bottom: var(--spacing-xs);
        }
        
        .settings-description {
            font-size: 0.9rem;
            color: var(--color-text-secondary);
            margin-bottom: var(--spacing-sm);
        }
        
        .settings-actions {
            margin-top: var(--spacing-lg);
            display: flex;
            justify-content: flex-end;
            gap: var(--spacing-sm);
        }
        </style>
        """, unsafe_allow_html=True)

# 获取组件样式类
def get_component_class(component_type, variant=None):
    """获取组件样式类"""
    classes = {
        "card": "card",
        "button": "stButton",
        "input": "stTextInput",
        "select": "stSelectbox",
        "slider": "stSlider",
        "table": "stDataFrame",
        "stage_card": "card stage-card",
        "metric_card": "metric-card",
        "chart_container": "chart-container",
        "file_info_card": "file-info-card",
        "code_block": "code-block"
    }
    
    # 添加变体
    if variant:
        if component_type == "stage_card":
            return f"{classes[component_type]} stage-{variant}"
        elif component_type == "button":
            return f"{classes[component_type]} button-{variant}"
    
    return classes.get(component_type, "")

# 生成内联样式
def generate_inline_style(style_dict):
    """生成内联样式字符串"""
    style_str = ""
    for prop, value in style_dict.items():
        style_str += f"{prop}: {value}; "
    return style_str