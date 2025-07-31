#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 首页

显示欢迎信息和文件上传界面
增强版本：实现更现代化的UI和更好的用户体验
"""

import streamlit as st
import pandas as pd
import io
import os
from state import reset_all_stages
from components.widgets import apply_global_styles, file_uploader_card, metric_card
from components.feedback import loading_spinner, success_notification, error_notification, animated_container, button_with_loading
from utils.helpers import truncate_text, get_table_download_link

def render():
    """渲染增强版首页"""
    # 应用全局样式
    apply_global_styles()
    
    # 主标题
    st.markdown('<h1 class="main-header">📊 Excel智能体</h1>', unsafe_allow_html=True)
    
    # 创建两列布局
    welcome_col, upload_col = st.columns([3, 2])
    
    with welcome_col:
        render_welcome_section()
    
    with upload_col:
        render_file_upload_section()
    
    # 如果已上传文件，显示文件预览
    if st.session_state.uploaded_file_data is not None:
        try:
            render_file_preview_section()
        except Exception as e:
            st.error(f"文件预览显示错误: {str(e)}")
            st.warning("请尝试重新上传文件")
            # 提供重置按钮
            if st.button("重置上传状态"):
                st.session_state.uploaded_file_data = None

def render_welcome_section():
    """渲染欢迎信息部分"""
    st.markdown("""
    <div class="card">
        <div class="card-header">👋 欢迎使用Excel智能体</div>
        <p>Excel智能体是一个强大的数据分析工具，可以帮助您快速分析Excel数据并生成洞察。</p>
        
        <h3>🚀 主要功能</h3>
        <ul>
            <li><strong>数据摘要</strong> - 自动生成数据统计摘要</li>
            <li><strong>智能分析</strong> - 基于AI的数据分析和可视化</li>
            <li><strong>自定义图表</strong> - 创建自定义数据可视化</li>
            <li><strong>参数调整</strong> - 控制AI生成结果的精确度</li>
        </ul>
        
        <h3>📝 使用方法</h3>
        <ol>
            <li>上传Excel文件</li>
            <li>选择要分析的工作表</li>
            <li>输入分析问题</li>
            <li>查看生成的分析结果和图表</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

def render_file_upload_section():
    """渲染文件上传部分"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📁 文件上传</div>', unsafe_allow_html=True)
    
    # 文件上传区域
    uploaded_file = st.file_uploader(
        "上传Excel文件",
        type=["xlsx", "xls"],
        help="支持.xlsx和.xls格式",
        key="excel_uploader"
    )
    
    # 文件格式信息
    st.markdown("""
    <div style="font-size: 0.9rem; color: #6c757d; margin-top: 0.5rem;">
        <strong>支持的格式:</strong> .xlsx, .xls<br>
        <strong>最大文件大小:</strong> 200MB
    </div>
    """, unsafe_allow_html=True)
    
    # 示例文件下载
    if os.path.exists("assets/example.xlsx"):
        with open("assets/example.xlsx", "rb") as file:
            st.download_button(
                label="📥 下载示例文件",
                data=file,
                file_name="example.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="下载示例Excel文件以了解格式要求"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 处理上传的文件
    if uploaded_file is not None:
        process_uploaded_file(uploaded_file)

def process_uploaded_file(uploaded_file):
    """处理上传的Excel文件 - 简化版本"""
    
    try:
        # 显示处理信息
        st.info("📂 正在处理Excel文件...")
        
        # 读取Excel文件
        excel_file = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
        sheet_names = excel_file.sheet_names
        
        # 工作表选择
        if len(sheet_names) > 1:
            st.markdown("#### 📋 工作表选择")
            
            # 显示工作表选择
            selected_sheet = st.selectbox(
                "选择要分析的工作表:",
                sheet_names,
                help=f"文件包含 {len(sheet_names)} 个工作表，请选择要分析的工作表"
            )
            
            st.success(f"✅ 已选择工作表: **{selected_sheet}**")
        else:
            selected_sheet = sheet_names[0]
            st.info(f"📋 检测到单个工作表: **{selected_sheet}**")
        
        # 读取数据
        st.info("📈 正在读取数据...")
        df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), sheet_name=selected_sheet)
        
        # 简单的数据清理
        cleaned_df = df.copy()
        
        # 处理包含混合类型的列
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                cleaned_df[col] = cleaned_df[col].astype(str)
                cleaned_df[col] = cleaned_df[col].replace('nan', '')
        
        # 准备文件数据
        file_data = {
            'filename': uploaded_file.name,
            'dataframe': df.to_dict('records'),
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'dtypes': df.dtypes.astype(str).to_dict(),
            'current_sheet': selected_sheet,
            'sheet_names': sheet_names,
            'cleaned_df': cleaned_df
        }
        
        # 存储到session state
        st.session_state.uploaded_file_data = file_data
        
        # 显示成功信息
        st.success(f"✅ 文件上传成功: {uploaded_file.name}")
        st.info("ℹ️ 文件处理完成，请查看下方的文件预览")
        
    except Exception as e:
        # 显示错误信息
        st.error(f"❌ 文件处理错误: {str(e)}")
        st.session_state.uploaded_file_data = None
        
        # 重置所有阶段状态
        reset_all_stages()

def render_file_preview_section():
    """渲染文件预览部分"""
    try:
        file_data = st.session_state.uploaded_file_data
        
        if not file_data:
            st.warning("⚠️ 文件数据为空")
            return
        
        # 验证文件数据完整性
        if not isinstance(file_data, dict) or 'filename' not in file_data:
            st.error("❌ 文件数据损坏，请重新上传文件")
            st.session_state.uploaded_file_data = None
            return

        # 简单的文件预览标题
        st.markdown("---")
        st.markdown("### 📋 文件预览")
        
        # 文件基本信息 - 不使用动画容器
        st.markdown("#### 📊 文件信息")
        
        # 显示文件基本信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("数据行数", file_data['shape'][0])
        with col2:
            st.metric("数据列数", file_data['shape'][1])
        with col3:
            st.metric("工作表数", len(file_data['sheet_names']))
        
        # 显示列信息
        with st.expander("📊 列信息详情", expanded=False):
            try:
                df = pd.DataFrame(file_data['dataframe'])
                col_info = []
                for i, col in enumerate(df.columns):
                    dtype = str(df[col].dtype)
                    non_null = df[col].count()
                    null_count = df[col].isnull().sum()
                    null_pct = (null_count / len(df)) * 100 if len(df) > 0 else 0
                    
                    col_info.append(f"• **{col}** ({dtype}) - {non_null} 非空值, {null_count} 缺失值 ({null_pct:.1f}%)")
                
                st.markdown("\n".join(col_info))
            except Exception as e:
                st.warning(f"列信息显示错误: {str(e)}")
        
        # 数据预览 - 简化版本
        st.markdown("#### 👀 数据预览")
        
        try:
            # 使用最简单的方式显示数据
            df = pd.DataFrame(file_data['dataframe'])
            display_df = df.head(5)  # 只显示前5行
            
            st.dataframe(display_df, use_container_width=True, height=200)
            
        except Exception as e:
            st.warning(f"数据预览显示错误: {str(e)}")
            # 备选方案：显示基本信息
            st.text(f"数据预览：{file_data['shape'][0]} 行 × {file_data['shape'][1]} 列")
            st.text("列名：" + ", ".join([str(col)[:20] for col in file_data['columns'][:5]]))
            if len(file_data['columns']) > 5:
                st.text(f"... 还有 {len(file_data['columns']) - 5} 列")
        
        # 文件验证结果 - 简化版本
        st.markdown("#### ✅ 文件验证")
        
        validation_results = validate_file(file_data)
        
        for result in validation_results:
            if result['status'] == 'success':
                st.success(result['message'])
            elif result['status'] == 'warning':
                st.warning(result['message'])
            elif result['status'] == 'error':
                st.error(result['message'])
        
        # 开始分析按钮 - 简化版本
        st.markdown("---")
        st.markdown("### 🚀 开始分析")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # 使用简单按钮而不是带加载状态的按钮
            if st.button("开始分析数据", key="start_analysis_simple_btn"):
                # 重置所有阶段状态
                reset_all_stages()
                # 显示成功消息，避免直接修改sidebar_selection导致冲突
                st.success("✅ 分析环境准备完成！请点击侧边栏的\"数据分析\"开始分析。")
        
        with col2:
            st.info("点击按钮开始分析，或者从侧边栏选择\"数据分析\"")
            
    except Exception as e:
        st.error(f"文件预览渲染错误: {str(e)}")
        st.code(str(e))  # 显示完整错误信息
        if st.button("清除文件数据"):
            st.session_state.uploaded_file_data = None
            # 不需要手动调用st.rerun()，Streamlit会自动重新运行

def validate_file(file_data):
    """验证文件数据"""
    results = []
    
    # 检查行数
    if file_data['shape'][0] == 0:
        results.append({
            'status': 'error',
            'message': '文件不包含任何数据行'
        })
    elif file_data['shape'][0] < 5:
        results.append({
            'status': 'warning',
            'message': f'文件只包含 {file_data["shape"][0]} 行数据，可能不足以进行有意义的分析'
        })
    else:
        results.append({
            'status': 'success',
            'message': f'文件包含 {file_data["shape"][0]} 行数据，足够进行分析'
        })
    
    # 检查列数
    if file_data['shape'][1] == 0:
        results.append({
            'status': 'error',
            'message': '文件不包含任何数据列'
        })
    elif file_data['shape'][1] < 2:
        results.append({
            'status': 'warning',
            'message': '文件只包含1列数据，可能无法进行关联分析'
        })
    else:
        results.append({
            'status': 'success',
            'message': f'文件包含 {file_data["shape"][1]} 列数据'
        })
    
    # 检查数据类型
    df = pd.DataFrame(file_data['dataframe'])
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) == 0:
        results.append({
            'status': 'warning',
            'message': '文件不包含数值类型列，可能无法进行数值分析'
        })
    else:
        results.append({
            'status': 'success',
            'message': f'文件包含 {len(numeric_cols)} 个数值类型列，可以进行数值分析'
        })
    
    # 检查缺失值
    missing_values = df.isnull().sum().sum()
    if missing_values > 0:
        missing_pct = (missing_values / (df.shape[0] * df.shape[1])) * 100
        if missing_pct > 50:
            results.append({
                'status': 'error',
                'message': f'文件包含大量缺失值 ({missing_pct:.1f}%)，可能影响分析质量'
            })
        elif missing_pct > 20:
            results.append({
                'status': 'warning',
                'message': f'文件包含较多缺失值 ({missing_pct:.1f}%)，可能需要数据清理'
            })
        else:
            results.append({
                'status': 'warning',
                'message': f'文件包含少量缺失值 ({missing_pct:.1f}%)，分析时将自动处理'
            })
    else:
        results.append({
            'status': 'success',
            'message': '文件不包含缺失值，数据完整'
        })
    
    return results