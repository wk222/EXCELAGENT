#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 状态管理

负责初始化和管理应用的状态，包括会话状态和用户偏好设置
"""

import streamlit as st
import json
import os
from datetime import datetime

# 常量定义
DEFAULT_LLM_SETTINGS = {
    'model': 'grok-3-mini',
    'temperature': 0.7,
    'max_tokens': 2000,
    'api_key': '',
    'base_url': 'http://48.210.12.198:3000/v1',
    'timeout': 60,
    'retries': 2,
    'top_p': 1.0,
    'frequency_penalty': 0.0,
    'presence_penalty': 0.0,
    'stop_sequences': [],
    'remember_settings': True
}

DEFAULT_UI_PREFERENCES = {
    'theme': 'light',
    'default_chart_type': 'auto',
    'sidebar_expanded': True,
    'show_code': False,
    'auto_run_analysis': False
}

# 设置文件路径
SETTINGS_DIR = '.kiro/settings'
LLM_SETTINGS_FILE = os.path.join(SETTINGS_DIR, 'llm_settings.json')
UI_SETTINGS_FILE = os.path.join(SETTINGS_DIR, 'ui_preferences.json')

def initialize_state():
    """初始化应用状态"""
    # 确保设置目录存在
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    
    # 导航状态
    if 'sidebar_selection' not in st.session_state:
        st.session_state.sidebar_selection = "首页"
    
    # 文件上传状态
    if 'uploaded_file_data' not in st.session_state:
        st.session_state.uploaded_file_data = None
    
    # 分析阶段状态
    initialize_analysis_state()
    
    # 自定义图表状态
    if 'custom_charts' not in st.session_state:
        st.session_state.custom_charts = []
    
    # 加载LLM设置
    if 'llm_settings' not in st.session_state:
        st.session_state.llm_settings = load_llm_settings()
    
    # 加载UI偏好设置
    if 'ui_preferences' not in st.session_state:
        st.session_state.ui_preferences = load_ui_preferences()
    
    # 会话历史
    if 'session_history' not in st.session_state:
        st.session_state.session_history = []
    
    # 会话ID
    if 'session_id' not in st.session_state:
        st.session_state.session_id = generate_session_id()
    
    # 应用状态
    if 'app_state' not in st.session_state:
        st.session_state.app_state = {
            'is_processing': False,
            'last_action': None,
            'last_action_time': None,
            'error': None
        }

def initialize_analysis_state():
    """初始化分析状态"""
    # 阶段一：数据摘要
    if 'stage1_completed' not in st.session_state:
        st.session_state.stage1_completed = False
    if 'stage1_result' not in st.session_state:
        st.session_state.stage1_result = None
    
    # 阶段二：数据处理与预分析
    if 'stage2_completed' not in st.session_state:
        st.session_state.stage2_completed = False
    if 'stage2_result' not in st.session_state:
        st.session_state.stage2_result = None
    if 'stage2_generated_code' not in st.session_state:
        st.session_state.stage2_generated_code = None
    if 'stage2_question' not in st.session_state:
        st.session_state.stage2_question = ""
    
    # 阶段三：深度智能分析
    if 'stage3_completed' not in st.session_state:
        st.session_state.stage3_completed = False
    if 'stage3_result' not in st.session_state:
        st.session_state.stage3_result = None
    if 'stage3_question' not in st.session_state:
        st.session_state.stage3_question = ""

def reset_all_stages():
    """重置所有分析阶段状态"""
    keys_to_reset = [
        'stage1_completed', 'stage1_result', 
        'stage2_completed', 'stage2_result', 'stage2_generated_code', 'stage2_question',
        'stage3_completed', 'stage3_result', 'stage3_question'
    ]
    for key in keys_to_reset:
        if 'result' in key or 'code' in key:
            st.session_state[key] = None
        elif 'question' in key:
            st.session_state[key] = ""
        else:
            st.session_state[key] = False
    
    # 记录操作
    log_action("reset_all_stages")

def reset_stage1():
    """重置阶段一及后续"""
    reset_all_stages()
    log_action("reset_stage1")

def reset_stage2():
    """重置阶段二及后续"""
    keys_to_reset = [
        'stage2_completed', 'stage2_result', 'stage2_generated_code', 'stage2_question',
        'stage3_completed', 'stage3_result', 'stage3_question'
    ]
    for key in keys_to_reset:
        if 'result' in key or 'code' in key:
            st.session_state[key] = None
        elif 'question' in key:
            st.session_state[key] = ""
        else:
            st.session_state[key] = False
    
    log_action("reset_stage2")

def reset_stage3():
    """重置阶段三"""
    st.session_state.stage3_completed = False
    st.session_state.stage3_result = None
    st.session_state.stage3_question = ""
    
    log_action("reset_stage3")

def update_llm_settings(settings):
    """更新LLM设置并保存到文件"""
    st.session_state.llm_settings.update(settings)
    
    # 只有当设置了记住设置时才保存到文件
    if st.session_state.llm_settings.get('remember_settings', True):
        save_llm_settings()
    
    log_action("update_llm_settings", {"updated_keys": list(settings.keys())})
    
def update_llm_parameter(param_name, value):
    """更新单个LLM参数"""
    if param_name in st.session_state.llm_settings:
        st.session_state.llm_settings[param_name] = value
        
        # 只有当设置了记住设置时才保存到文件
        if st.session_state.llm_settings.get('remember_settings', True):
            save_llm_settings()
        
        log_action("update_llm_parameter", {"param": param_name, "value": value})
        return True
    return False

def update_llm_temperature(value):
    """更新LLM温度参数"""
    if 0.0 <= value <= 1.0:
        return update_llm_parameter('temperature', value)
    return False

def update_llm_max_tokens(value):
    """更新LLM最大令牌数"""
    if value > 0:
        return update_llm_parameter('max_tokens', value)
    return False

def update_llm_model(model_name):
    """更新LLM模型"""
    return update_llm_parameter('model', model_name)

def toggle_llm_settings_persistence(remember=True):
    """切换LLM设置持久化"""
    update_llm_parameter('remember_settings', remember)
    
    # 如果开启了持久化，立即保存当前设置
    if remember:
        save_llm_settings()
    # 如果关闭了持久化，可以选择删除设置文件
    elif os.path.exists(LLM_SETTINGS_FILE) and not remember:
        try:
            os.remove(LLM_SETTINGS_FILE)
            log_action("delete_llm_settings_file")
        except Exception as e:
            print(f"删除LLM设置文件失败: {e}")
    
    return remember

def update_ui_preferences(preferences):
    """更新UI偏好设置并保存到文件"""
    st.session_state.ui_preferences.update(preferences)
    save_ui_preferences()
    log_action("update_ui_preferences")

def get_llm_settings():
    """获取当前LLM设置"""
    return st.session_state.llm_settings

def get_ui_preferences():
    """获取当前UI偏好设置"""
    return st.session_state.ui_preferences

def load_llm_settings():
    """从文件加载LLM设置"""
    try:
        if os.path.exists(LLM_SETTINGS_FILE):
            with open(LLM_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return DEFAULT_LLM_SETTINGS.copy()
    except Exception as e:
        print(f"加载LLM设置失败: {e}")
        return DEFAULT_LLM_SETTINGS.copy()

def load_ui_preferences():
    """从文件加载UI偏好设置"""
    try:
        if os.path.exists(UI_SETTINGS_FILE):
            with open(UI_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return DEFAULT_UI_PREFERENCES.copy()
    except Exception as e:
        print(f"加载UI偏好设置失败: {e}")
        return DEFAULT_UI_PREFERENCES.copy()

def save_llm_settings():
    """保存LLM设置到文件"""
    try:
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        with open(LLM_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.llm_settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存LLM设置失败: {e}")

def save_ui_preferences():
    """保存UI偏好设置到文件"""
    try:
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        with open(UI_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.ui_preferences, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存UI偏好设置失败: {e}")

def generate_session_id():
    """生成唯一的会话ID"""
    import uuid
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"session_{timestamp}_{unique_id}"

def log_action(action_name, details=None):
    """记录用户操作"""
    if 'session_history' not in st.session_state:
        st.session_state.session_history = []
    
    action_log = {
        'action': action_name,
        'timestamp': datetime.now().isoformat(),
        'details': details
    }
    
    st.session_state.session_history.append(action_log)
    
    # 更新最后操作状态
    st.session_state.app_state['last_action'] = action_name
    st.session_state.app_state['last_action_time'] = datetime.now().isoformat()

def set_processing_state(is_processing, error=None):
    """设置处理状态"""
    st.session_state.app_state['is_processing'] = is_processing
    if error:
        st.session_state.app_state['error'] = error
    elif not is_processing:
        st.session_state.app_state['error'] = None

def is_processing():
    """检查是否正在处理"""
    return st.session_state.app_state.get('is_processing', False)

def get_error():
    """获取错误信息"""
    return st.session_state.app_state.get('error')

def clear_error():
    """清除错误信息"""
    st.session_state.app_state['error'] = None

def export_llm_settings_as_dict():
    """导出LLM设置为字典格式，可用于其他组件"""
    if 'llm_settings' not in st.session_state:
        return load_llm_settings()
    return st.session_state.llm_settings.copy()

def get_llm_parameter(param_name, default=None):
    """获取特定LLM参数值"""
    if 'llm_settings' not in st.session_state:
        llm_settings = load_llm_settings()
    else:
        llm_settings = st.session_state.llm_settings
    
    return llm_settings.get(param_name, default)