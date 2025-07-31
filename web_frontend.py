#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 分阶段执行版本

左侧：文件上传和数据预览
右侧：分阶段执行功能（阶段一 → 阶段二 → 阶段三）
"""

import streamlit as st
import pandas as pd
import json
import plotly.io as pio
import base64
import io
import logging

# 导入模块化的核心函数
from excel_mcp_server import (
    analyze_excel_data_core,
    generate_visualizations_only_core,
    get_data_summary_core,
    execute_custom_code_core,
    generate_deep_analysis_core  # 添加阶段三专用函数
)

# 配置页面
st.set_page_config(
    page_title="Excel智能体 - 分阶段执行",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stage-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2e8b57;
        margin: 1rem 0;
        padding: 0.5rem;
        border-left: 4px solid #2e8b57;
        background-color: #f0f8f0;
    }
    .stage-completed {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stage-pending {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stage-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'uploaded_file_data' not in st.session_state:
    st.session_state.uploaded_file_data = None
if 'stage1_completed' not in st.session_state:
    st.session_state.stage1_completed = False
if 'stage1_result' not in st.session_state:
    st.session_state.stage1_result = None
if 'stage2_completed' not in st.session_state:
    st.session_state.stage2_completed = False
if 'stage2_result' not in st.session_state:
    st.session_state.stage2_result = None
if 'stage2_generated_code' not in st.session_state:
    st.session_state.stage2_generated_code = None
if 'stage3_completed' not in st.session_state:
    st.session_state.stage3_completed = False
if 'stage3_result' not in st.session_state:
    st.session_state.stage3_result = None

def main():
    # 主标题
    st.markdown('<h1 class="main-header">📊 Excel智能体 - 分阶段执行</h1>', unsafe_allow_html=True)
    
    # 创建左右两列布局
    left_col, right_col = st.columns([1.3, 1])
    
    with left_col:
        show_file_upload_and_preview()
    
    with right_col:
        show_stage_execution()

def show_file_upload_and_preview():
    """显示文件上传和数据预览区域"""
    st.markdown("## 📁 文件上传与数据预览")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "上传Excel文件",
        type=["xlsx", "xls"],
        help="支持.xlsx和.xls格式",
        key="excel_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # 读取Excel文件
            excel_file = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
            sheet_names = excel_file.sheet_names
            
            # 工作表选择
            if len(sheet_names) > 1:
                st.markdown("#### 📋 工作表选择")
                
                # 显示所有工作表的基本信息
                with st.expander("📊 所有工作表信息", expanded=False):
                    for i, sheet in enumerate(sheet_names):
                        try:
                            temp_df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), sheet_name=sheet, nrows=0)
                            st.text(f"{i+1}. {sheet}: {len(temp_df.columns)} 列")
                        except:
                            st.text(f"{i+1}. {sheet}: 读取失败")
                
                selected_sheet = st.selectbox(
                    "选择要分析的工作表:",
                    sheet_names,
                    help=f"文件包含 {len(sheet_names)} 个工作表，请选择要分析的工作表"
                )
                
                # 显示选中工作表的详细信息
                st.success(f"✅ 已选择工作表: **{selected_sheet}**")
                
            else:
                selected_sheet = sheet_names[0]
                st.info(f"📋 单个工作表: **{selected_sheet}**")
            
            # 读取数据
            df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), sheet_name=selected_sheet)
            
            # 数据清理：处理混合类型列和特殊字符
            cleaned_df = df.copy()
            clean_column_mapping = {}
            
            # 处理包含混合类型的列
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype == 'object':
                    # 将所有object类型列转换为字符串，避免混合类型问题
                    cleaned_df[col] = cleaned_df[col].astype(str)
                    # 替换nan字符串
                    cleaned_df[col] = cleaned_df[col].replace('nan', '')
            
            # 清理列名（移除特殊字符）
            original_columns = cleaned_df.columns.tolist()
            for i, col in enumerate(original_columns):
                if pd.isna(col) or str(col).startswith('Unnamed:') or str(col).strip() == '':
                    new_name = f"列{i+1}"
                    clean_column_mapping[col] = new_name
                    cleaned_df.rename(columns={col: new_name}, inplace=True)
                else:
                    # 即使是正常列名也记录，方便后续显示
                    clean_column_mapping[col] = str(col)
            
            # 准备文件数据（使用原始数据）
            file_data = {
                'filename': uploaded_file.name,
                'dataframe': df.to_dict('records'),  # 使用原始数据
                'columns': df.columns.tolist(),      # 使用原始列名
                'shape': df.shape,
                'dtypes': df.dtypes.astype(str).to_dict(),
                'current_sheet': selected_sheet,
                'sheet_names': sheet_names
            }
            
            # 存储到session state
            st.session_state.uploaded_file_data = file_data
            
            # 显示文件基本信息
            st.success(f"✅ 文件上传成功: {uploaded_file.name}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("数据行数", df.shape[0])
            with col2:
                st.metric("数据列数", df.shape[1])
            with col3:
                st.metric("工作表数", len(sheet_names))
            
            # 数据预览
            st.markdown("### 📋 数据预览")
            
            # 显示列信息
            with st.expander("📊 列信息", expanded=True):
                col_info = []
                for i, col in enumerate(df.columns):
                    dtype = str(df[col].dtype)
                    non_null = df[col].count()
                    display_name = clean_column_mapping.get(col, col) if col in clean_column_mapping else col
                    col_info.append(f"• **{display_name}** ({dtype}) - {non_null} 非空值")
                st.markdown("\n".join(col_info))
            
            # 显示前几行数据
            with st.expander("👀 前5行数据", expanded=True):
                try:
                    # 使用清理后的数据显示，避免Arrow序列化问题
                    display_df = cleaned_df.head()
                    st.dataframe(display_df, use_container_width=True, height=200)
                except Exception as e:
                    # 如果仍然失败，使用最基础的文本显示
                    st.warning("数据包含特殊格式，使用文本模式显示")
                    try:
                        # 尝试生成简化的表格显示
                        preview_data = []
                        for i in range(min(5, len(df))):
                            row_data = {}
                            for col in df.columns[:10]:  # 限制列数避免显示过宽
                                display_name = clean_column_mapping.get(col, col) if col in clean_column_mapping else str(col)
                                value = str(df.iloc[i][col])[:50]  # 限制值长度
                                row_data[display_name] = value
                            preview_data.append(row_data)
                        
                        preview_df = pd.DataFrame(preview_data)
                        st.dataframe(preview_df, use_container_width=True, height=200)
                    except:
                        # 最终备选方案：简单文本
                        st.text(f"数据预览：{df.shape[0]} 行 × {df.shape[1]} 列")
                        st.text("列名：" + ", ".join([str(col)[:20] for col in df.columns[:10]]))
                        if len(df.columns) > 10:
                            st.text(f"... 还有 {len(df.columns) - 10} 列")
                
        except Exception as e:
            st.error(f"❌ 文件处理错误: {str(e)}")
            st.session_state.uploaded_file_data = None
    else:
        st.info("👆 请上传Excel文件开始分析")
        st.session_state.uploaded_file_data = None
        # 重置所有阶段状态
        reset_all_stages()

def show_stage_execution():
    """显示分阶段执行区域"""
    st.markdown("## 🚀 分阶段执行")
    
    if st.session_state.uploaded_file_data is None:
        st.warning("⚠️ 请先上传Excel文件")
        return
    
    # 阶段一：数据摘要
    show_stage1()
    
    # 阶段二：分析处理
    show_stage2()
    
    # 阶段三：完整分析
    show_stage3()
    
    # 自定义图表面板
    st.markdown("---")  # 分隔线
    show_custom_chart_panel()

def show_stage1():
    """阶段一：数据摘要"""
    st.markdown('<div class="stage-header">📊 阶段一：数据摘要</div>', unsafe_allow_html=True)
    
    if not st.session_state.stage1_completed:
        st.markdown('<div class="stage-pending">⏳ 待执行：获取数据统计摘要</div>', unsafe_allow_html=True)
        
        if st.button("🔍 执行阶段一", type="primary", key="stage1_btn"):
            with st.spinner("正在生成数据摘要..."):
                result = get_data_summary_core(st.session_state.uploaded_file_data)
                st.session_state.stage1_result = result
                st.session_state.stage1_completed = True
                st.rerun()
    else:
        # 显示阶段一结果
        result = st.session_state.stage1_result
        if result.status == "成功":
            st.markdown('<div class="stage-completed">✅ 阶段一完成</div>', unsafe_allow_html=True)
            
            with st.expander("📊 查看数据摘要"):
                st.text(result.data['summary'])
            
            if st.button("🔄 重置阶段一", key="stage1_reset"):
                reset_stage1()
                st.rerun()
        else:
            st.markdown(f'<div class="stage-error">❌ 阶段一失败：{result.message}</div>', unsafe_allow_html=True)
            
            # 显示详细错误信息
            if result.error:
                with st.expander("🔍 查看详细错误信息", expanded=True):
                    st.error("错误详情:")
                    st.code(result.error, language="text")
            
            if st.button("🔄 重试阶段一", key="stage1_retry"):
                reset_stage1()
                st.rerun()

def show_stage2():
    """阶段二：分析处理"""
    st.markdown('<div class="stage-header">⚙️ 阶段二：数据处理与预分析</div>', unsafe_allow_html=True)
    
    if not st.session_state.stage1_completed:
        st.markdown('<div class="stage-pending">⏸️ 请先完成阶段一</div>', unsafe_allow_html=True)
        return
    
    if not st.session_state.stage2_completed:
        st.markdown('<div class="stage-pending">⏳ 待执行：输入问题并选择处理方式</div>', unsafe_allow_html=True)
        
        # 首先输入问题
        question = st.text_input(
            "分析问题:",
            placeholder="例如：分析销售数据的趋势和异常",
            key="stage2_question"
        )
        
        if question:
            # 选择处理方式
            stage2_option = st.radio(
                "选择处理方式:",
                ["📊 智能综合分析（可视化+统计）", "💻 自定义代码"],
                key="stage2_option"
            )
            
            if stage2_option == "📊 智能综合分析（可视化+统计）":
                chart_type = st.selectbox("图表类型偏好:", ["auto", "bar", "line", "scatter", "pie"])
                
                if st.button("📈 生成分析", type="primary", key="stage2_analysis"):
                    with st.spinner("生成综合分析中..."):
                        # 获取数据摘要
                        data_summary = ""
                        if st.session_state.stage1_result and st.session_state.stage1_result.data:
                            data_summary = st.session_state.stage1_result.data.get('summary', '')
                        
                        # 创建一个简化的阶段2结果：只执行代码，不生成AI摘要
                        try:
                            # 导入必要的模块
                            from excel_mcp_server import DataAnalyzer, CodeGenerator, CodeExecutor, AnalysisResult
                            import pandas as pd
                            
                            # 重建DataFrame
                            df = pd.DataFrame(st.session_state.uploaded_file_data['dataframe'])
                            
                            # 生成分析代码（但不生成摘要）
                            enhanced_question = f"【阶段二预分析】{question}\n\n请生成既包含可视化图表又包含统计分析的代码，重点关注有助于后续深度分析的数据洞察。"
                            analysis_code = CodeGenerator.generate_analysis_code(enhanced_question, data_summary, "df")
                            
                            # 执行代码
                            execution_results = CodeExecutor.execute_code(analysis_code, df, "df")
                            
                            # 构建简化的结果（不包含AI生成的详细摘要）
                            result_data = {
                                "question": question,
                                "generated_code": analysis_code,
                                "execution_results": execution_results,
                                "summary": f"✅ 阶段二代码执行完成，生成了{len(execution_results.get('plotly_figures', []))}个图表"
                            }
                            
                            # 创建简化的结果对象
                            status = "成功" if not execution_results.get("error") else "部分成功"
                            result = AnalysisResult(
                                status=status,
                                message=f"阶段二完成，生成了{len(execution_results.get('plotly_figures', []))}个图表",
                                data=result_data,
                                error=execution_results.get("error")
                            )
                            
                            st.session_state.stage2_result = result
                            st.session_state.stage2_completed = True
                            st.rerun()
                            
                        except Exception as e:
                            # 如果简化流程失败，显示错误
                            st.error(f"阶段二执行失败: {str(e)}")
                            result = AnalysisResult(
                                status="失败",
                                message="阶段二代码生成或执行失败",
                                error=str(e)
                            )
                            st.session_state.stage2_result = result
                            st.session_state.stage2_completed = True
                            st.rerun()
                        
            else:
                custom_code = st.text_area(
                    "Python代码:",
                    value="print('数据形状:', df.shape)\nprint(df.describe())",
                    height=100
                )
                
                if st.button("▶️ 执行代码", type="primary", key="stage2_code"):
                    with st.spinner("执行代码中..."):
                        # 保存用户输入的代码和问题
                        
                        result = execute_custom_code_core(st.session_state.uploaded_file_data, custom_code)
                        st.session_state.stage2_result = result
                        st.session_state.stage2_completed = True
                        st.rerun()
        else:
            st.info("👆 请先输入您要分析的问题")
            
    else:
        # 显示阶段二结果
        result = st.session_state.stage2_result
        question = st.session_state.get('stage2_question', '')
        
        if result.status in ["成功", "部分成功"]:
            st.markdown('<div class="stage-completed">✅ 阶段二完成</div>', unsafe_allow_html=True)
            
            # 显示问题信息
            if question:
                with st.expander("🤔 分析问题", expanded=True):
                    st.markdown(f"**问题:** {question}")
            
            # 显示分析结果
            if result.data:
                # 显示分析摘要
                if result.data.get('summary'):
                    with st.expander("📊 预分析摘要", expanded=True):
                        st.markdown(result.data['summary'])
                
                # 显示执行结果
                exec_results = result.data.get('execution_results', {})
                if exec_results.get('stdout'):
                    with st.expander("📈 统计分析结果", expanded=True):
                        st.text(exec_results['stdout'])
                
                # 显示图表
                charts = exec_results.get('plotly_figures', [])
                if charts:
                    with st.expander(f"📊 可视化图表 ({len(charts)}个)", expanded=True):
                        for i, chart_json in enumerate(charts):
                            try:
                                fig = pio.from_json(chart_json)
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.error(f"图表 {i+1} 显示失败: {str(e)}")
                
                # 显示生成的代码
                if result.data.get('generated_code'):
                    with st.expander("💻 查看生成的分析代码"):
                        st.code(result.data['generated_code'], language='python')
            
            if st.button("🔄 重置阶段二", key="stage2_reset"):
                reset_stage2()
                st.rerun()
        else:
            st.markdown(f'<div class="stage-error">❌ 阶段二失败：{result.message}</div>', unsafe_allow_html=True)
            
            # 显示详细错误信息
            if result.error:
                with st.expander("🔍 查看详细错误信息", expanded=True):
                    st.error("错误详情:")
                    st.code(result.error, language="text")
            
            if st.button("🔄 重试阶段二", key="stage2_retry"):
                reset_stage2()
                st.rerun()

def show_stage3():
    """阶段三：深度分析"""
    st.markdown('<div class="stage-header">🎯 阶段三：深度智能分析</div>', unsafe_allow_html=True)
    
    if not st.session_state.stage2_completed:
        st.markdown('<div class="stage-pending">⏸️ 请先完成阶段二</div>', unsafe_allow_html=True)
        return
    
    if not st.session_state.stage3_completed:
        st.markdown('<div class="stage-pending">⏳ 待执行：基于预分析的深度分析</div>', unsafe_allow_html=True)
        
        # 显示阶段二的问题作为上下文
        stage2_question = st.session_state.get('stage2_question', '')
        if stage2_question:
            st.info(f"📌 阶段二分析问题：{stage2_question}")
        
        question = st.text_input(
            "深度分析问题:",
            placeholder="例如：基于预分析结果，进一步探索异常原因和业务建议",
            help="可以基于阶段二的分析结果提出更深入的问题"
        )
        
        if st.button("🧠 开始深度分析", type="primary", key="stage3_btn", disabled=not question):
            with st.spinner("深度智能分析中..."):
                # 构建包含前面阶段信息的完整问题
                enhanced_question = f"【阶段三深度分析】{question}\n\n"
                
                # 添加阶段1信息
                if st.session_state.stage1_result and st.session_state.stage1_result.status == "成功":
                    enhanced_question += "[前序分析信息]\n阶段一已完成：数据摘要分析\n"
                
                # 添加阶段2信息
                if st.session_state.stage2_result and st.session_state.stage2_result.status in ["成功", "部分成功"]:
                    enhanced_question += f"阶段二已完成：针对问题'{stage2_question}'的预分析，包含可视化和统计分析\n"
                    
                    # 如果有阶段2的分析摘要，加入上下文
                    if st.session_state.stage2_result.data and st.session_state.stage2_result.data.get('summary'):
                        stage2_summary = st.session_state.stage2_result.data['summary'][:500]  # 限制长度
                        enhanced_question += f"阶段二分析摘要（节选）：{stage2_summary}\n"
                
                enhanced_question += "\n请基于以上已完成的分析步骤和发现，进行更深入的分析和洞察挖掘。重点关注业务含义、潜在问题和actionable建议。"
                
                # 获取数据摘要
                data_summary = ""
                if st.session_state.stage1_result and st.session_state.stage1_result.data:
                    data_summary = st.session_state.stage1_result.data.get('summary', '')
                
                # 调用阶段三深度分析函数（不生成代码，只分析已有结果）
                result = generate_deep_analysis_core(
                    stage2_question=stage2_question,
                    stage3_question=question,  # 用户在阶段三输入的问题
                    stage2_result=st.session_state.stage2_result,  # 阶段二的完整结果
                    data_summary=data_summary
                )
                st.session_state.stage3_result = result
                st.session_state.stage3_question = question  # 保存问题
                st.session_state.stage3_completed = True
                st.rerun()
    else:
        # 显示阶段三结果
        result = st.session_state.stage3_result
        stage3_question = st.session_state.get('stage3_question', '')
        stage2_question = st.session_state.get('stage2_question', '')
        
        if result.status in ["成功", "部分成功"]:
            st.markdown('<div class="stage-completed">✅ 阶段三完成</div>', unsafe_allow_html=True)
            
            if result.data:
                # 显示问题信息
                with st.expander("🤔 分析问题对比", expanded=True):
                    if stage2_question:
                        st.markdown(f"**阶段二问题:** {stage2_question}")
                    if stage3_question:
                        st.markdown(f"**阶段三问题:** {stage3_question}")
                
                with st.expander("🧠 深度分析摘要", expanded=True):
                    st.markdown(result.data.get('deep_analysis_report', '深度分析报告生成失败'))
                
                # 显示阶段二的图表（作为分析依据）
                stage2_charts_count = result.data.get('stage2_charts_count', 0)
                if stage2_charts_count > 0:
                    with st.expander(f"📊 阶段二生成的图表 ({stage2_charts_count}个) - 分析依据", expanded=False):
                        st.info("📌 以下图表是在阶段二生成的，深度分析报告基于这些图表")
                        # 从阶段二结果中获取图表
                        if st.session_state.stage2_result and st.session_state.stage2_result.data:
                            stage2_exec_results = st.session_state.stage2_result.data.get('execution_results', {})
                            charts = stage2_exec_results.get('plotly_figures', [])
                            for i, chart_json in enumerate(charts):
                                try:
                                    fig = pio.from_json(chart_json)
                                    st.plotly_chart(fig, use_container_width=True)
                                except Exception as e:
                                    st.error(f"图表 {i+1} 显示失败: {str(e)}")
                else:
                    st.info("📌 阶段二未生成图表")
                
                # 显示阶段二的简要摘要作为背景
                stage2_summary = result.data.get('stage2_summary', '')
                if stage2_summary:
                    with st.expander("📋 阶段二分析摘要（背景信息）", expanded=False):
                        st.markdown(stage2_summary)
            
            if st.button("🔄 重置阶段三", key="stage3_reset"):
                reset_stage3()
                st.rerun()
        else:
            st.markdown(f'<div class="stage-error">❌ 阶段三失败：{result.message}</div>', unsafe_allow_html=True)
            
            # 显示详细错误信息
            if result.error:
                with st.expander("🔍 查看详细错误信息", expanded=True):
                    st.error("错误详情:")
                    st.code(result.error, language="text")
            
            # 显示部分执行结果（如果有的话）
            if result.data:
                exec_results = result.data.get('execution_results', {})
                if exec_results.get('stderr'):
                    with st.expander("⚠️ 执行警告"):
                        st.text(exec_results['stderr'])
                if exec_results.get('stdout'):
                    with st.expander("📝 部分输出"):
                        st.text(exec_results['stdout'])
                if result.data.get('generated_code'):
                    with st.expander("💻 生成的代码"):
                        st.code(result.data['generated_code'], language='python')
            
            if st.button("🔄 重试阶段三", key="stage3_retry"):
                reset_stage3()
                st.rerun()

def reset_all_stages():
    """重置所有阶段"""
    keys_to_reset = [
        'stage1_completed', 'stage1_result', 
        'stage2_completed', 'stage2_result', 'stage2_generated_code',
        'stage3_completed', 'stage3_result'
    ]
    for key in keys_to_reset:
        if 'result' in key or 'code' in key:
            st.session_state[key] = None
        else:
            st.session_state[key] = False

def reset_stage1():
    """重置阶段一及后续"""
    reset_all_stages()

def reset_stage2():
    """重置阶段二及后续"""
    keys_to_reset = [
        'stage2_completed', 'stage2_result', 'stage2_generated_code',
        'stage3_completed', 'stage3_result'
    ]
    for key in keys_to_reset:
        if 'result' in key or 'code' in key:
            st.session_state[key] = None
        else:
            st.session_state[key] = False

def reset_stage3():
    """重置阶段三"""
    st.session_state.stage3_completed = False
    st.session_state.stage3_result = None

def show_custom_chart_panel():
    """显示自定义图表面板（类似Dash的交互式功能）"""
    st.markdown("## 🎨 自定义图表面板")
    
    if st.session_state.uploaded_file_data is None:
        st.warning("⚠️ 请先上传Excel文件")
        return
    
    # 重建DataFrame
    df = pd.DataFrame(st.session_state.uploaded_file_data['dataframe'])
    
    if df.empty:
        st.warning("⚠️ 数据为空")
        return
    
    st.markdown("### 🔧 图表配置")
    
    # 创建三列布局
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 图表类型选择
        chart_type = st.selectbox(
            "📊 图表类型",
            ["bar", "line", "scatter", "pie", "box", "violin", "histogram", "heatmap"],
            help="选择要生成的图表类型"
        )
    
    with col2:
        # X轴选择
        x_axis = st.selectbox(
            "📐 X轴",
            df.columns.tolist(),
            help="选择X轴数据列"
        )
    
    with col3:
        # Y轴选择（根据图表类型决定是否显示）
        if chart_type not in ["pie", "histogram"]:
            y_axis = st.selectbox(
                "📏 Y轴", 
                df.columns.tolist(),
                index=1 if len(df.columns) > 1 else 0,
                help="选择Y轴数据列"
            )
        else:
            y_axis = None
    
    # 高级选项
    with st.expander("🔧 高级选项", expanded=False):
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            # 颜色分组
            color_column = st.selectbox(
                "🎨 颜色分组 (可选)",
                ["无"] + df.columns.tolist(),
                help="根据此列的值进行颜色分组"
            )
            if color_column == "无":
                color_column = None
        
        with col_adv2:
            # 尺寸映射（仅对scatter图有效）
            if chart_type == "scatter":
                size_column = st.selectbox(
                    "⭕ 点大小映射 (可选)",
                    ["无"] + [col for col in df.columns if df[col].dtype in ['int64', 'float64']],
                    help="根据此列的值调整点的大小"
                )
                if size_column == "无":
                    size_column = None
            else:
                size_column = None
        
        # 图表标题
        chart_title = st.text_input(
            "📝 图表标题",
            value=f"{chart_type.title()} Chart: {x_axis}" + (f" vs {y_axis}" if y_axis else ""),
            help="自定义图表标题"
        )
        
        # 数据筛选
        st.markdown("#### 🔍 数据筛选")
        filter_enabled = st.checkbox("启用数据筛选")
        
        filtered_df = df.copy()
        if filter_enabled:
            # 数值范围筛选
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                filter_col = st.selectbox("筛选列", numeric_cols)
                min_val, max_val = st.slider(
                    f"{filter_col} 范围",
                    float(df[filter_col].min()),
                    float(df[filter_col].max()),
                    (float(df[filter_col].min()), float(df[filter_col].max()))
                )
                filtered_df = df[(df[filter_col] >= min_val) & (df[filter_col] <= max_val)]
                st.info(f"筛选后数据: {len(filtered_df)} 行 (原始: {len(df)} 行)")
    
    # 生成图表按钮
    if st.button("🎯 生成自定义图表", type="primary"):
        with st.spinner("生成图表中..."):
            try:
                import plotly.express as px
                import plotly.graph_objects as go
                
                # 根据图表类型生成对应图表
                if chart_type == "bar":
                    fig = px.bar(filtered_df, x=x_axis, y=y_axis, color=color_column, title=chart_title)
                elif chart_type == "line":
                    fig = px.line(filtered_df, x=x_axis, y=y_axis, color=color_column, title=chart_title)
                elif chart_type == "scatter":
                    fig = px.scatter(filtered_df, x=x_axis, y=y_axis, color=color_column, size=size_column, title=chart_title)
                elif chart_type == "pie":
                    fig = px.pie(filtered_df, names=x_axis, title=chart_title)
                elif chart_type == "box":
                    fig = px.box(filtered_df, x=x_axis, y=y_axis, color=color_column, title=chart_title)
                elif chart_type == "violin":
                    fig = px.violin(filtered_df, x=x_axis, y=y_axis, color=color_column, title=chart_title)
                elif chart_type == "histogram":
                    fig = px.histogram(filtered_df, x=x_axis, color=color_column, title=chart_title)
                elif chart_type == "heatmap":
                    # 对于热力图，需要数值型数据
                    numeric_df = filtered_df.select_dtypes(include=['number'])
                    if numeric_df.empty:
                        st.error("热力图需要数值型数据")
                        return
                    fig = px.imshow(numeric_df.corr(), title=f"相关性热力图 - {chart_title}")
                
                # 显示图表
                st.plotly_chart(fig, use_container_width=True)
                
                # 显示图表配置信息
                with st.expander("📋 图表配置信息"):
                    config_info = {
                        "图表类型": chart_type,
                        "X轴": x_axis,
                        "Y轴": y_axis if y_axis else "无",
                        "颜色分组": color_column if color_column else "无",
                        "数据行数": len(filtered_df)
                    }
                    if size_column:
                        config_info["尺寸映射"] = size_column
                    
                    for key, value in config_info.items():
                        st.text(f"{key}: {value}")
                
            except Exception as e:
                st.error(f"生成图表失败: {str(e)}")
                st.text("请检查数据类型和图表配置")

if __name__ == "__main__":
    main() 