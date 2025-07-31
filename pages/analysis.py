#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 数据分析页面

实现分阶段数据分析功能
"""

import streamlit as st
import plotly.io as pio
from state import reset_stage1, reset_stage2, reset_stage3

# 导入模块化的核心函数
from excel_mcp_server import (
    analyze_excel_data_core,
    generate_visualizations_only_core,
    get_data_summary_core,
    execute_custom_code_core,
    generate_deep_analysis_core
)

def render():
    """渲染数据分析页面"""
    # 主标题
    st.markdown('<h1 class="main-header">📊 Excel智能体 - 数据分析</h1>', unsafe_allow_html=True)
    
    if st.session_state.uploaded_file_data is None:
        st.warning("⚠️ 请先上传Excel文件")
        if st.button("返回上传页面"):
            st.session_state.sidebar_selection = "首页"
             
        return
    
    # 显示当前分析的文件信息
    file_data = st.session_state.uploaded_file_data
    st.info(f"📄 当前分析文件: **{file_data['filename']}** | 工作表: **{file_data['current_sheet']}** | 数据: {file_data['shape'][0]} 行 × {file_data['shape'][1]} 列")
    
    # 创建三个标签页
    tab1, tab2, tab3 = st.tabs(["📊 阶段一：数据摘要", "⚙️ 阶段二：数据处理与预分析", "🎯 阶段三：深度智能分析"])
    
    # 阶段一：数据摘要
    with tab1:
        show_stage1()
    
    # 阶段二：分析处理
    with tab2:
        show_stage2()
    
    # 阶段三：完整分析
    with tab3:
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
                 
    else:
        # 显示阶段一结果
        result = st.session_state.stage1_result
        if result.status == "成功":
            st.markdown('<div class="stage-completed">✅ 阶段一完成</div>', unsafe_allow_html=True)
            
            with st.expander("📊 查看数据摘要"):
                st.text(result.data['summary'])
            
            if st.button("🔄 重置阶段一", key="stage1_reset"):
                reset_stage1()
                 
        else:
            st.markdown(f'<div class="stage-error">❌ 阶段一失败：{result.message}</div>', unsafe_allow_html=True)
            
            # 显示详细错误信息
            if result.error:
                with st.expander("🔍 查看详细错误信息", expanded=True):
                    st.error("错误详情:")
                    st.code(result.error, language="text")
            
            if st.button("🔄 重试阶段一", key="stage1_retry"):
                reset_stage1()
                 

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
                # 获取LLM设置
                from state import get_llm_settings
                llm_settings = get_llm_settings()
                
                # 显示高级选项
                with st.expander("高级选项"):
                    chart_type = st.selectbox("图表类型偏好:", ["auto", "bar", "line", "scatter", "pie"])
                    temperature = st.slider(
                        "温度系数", 
                        min_value=0.0, 
                        max_value=1.0, 
                        value=llm_settings['temperature'],
                        step=0.1,
                        key="stage2_temperature_slider",
                        help="控制AI生成结果的创造性。较低的值使结果更确定，较高的值使结果更多样化。"
                    )
                
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
                         
        else:
            st.info("👆 请先输入您要分析的问题")
            
    else:
        # 显示阶段二结果
        result = st.session_state.stage2_result
        question = st.session_state.get('stage2_question', '')
        
        # 添加调试信息
        st.write("🔍 **调试信息:**")
        st.write(f"- result.status: `{result.status}`")
        st.write(f"- result.data 存在: `{result.data is not None}`")
        if result.data:
            st.write(f"- result.data keys: `{list(result.data.keys())}`")
            exec_results = result.data.get('execution_results', {})
            st.write(f"- execution_results keys: `{list(exec_results.keys())}`")
            charts = exec_results.get('plotly_figures', [])
            st.write(f"- 图表数量: `{len(charts)}`")
        st.markdown("---")
        
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
                 
        else:
            st.markdown(f'<div class="stage-error">❌ 阶段二失败：{result.message}</div>', unsafe_allow_html=True)
            
            # 显示详细错误信息
            if result.error:
                with st.expander("🔍 查看详细错误信息", expanded=True):
                    st.error("错误详情:")
                    st.code(result.error, language="text")
            
            if st.button("🔄 重试阶段二", key="stage2_retry"):
                reset_stage2()
                 

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
        
        # 获取LLM设置
        from state import get_llm_settings
        llm_settings = get_llm_settings()
        
        # 显示高级选项
        with st.expander("高级选项"):
            temperature = st.slider(
                "温度系数", 
                min_value=0.0, 
                max_value=1.0, 
                value=llm_settings['temperature'],
                step=0.1,
                key="stage3_temperature_slider",
                help="控制AI生成结果的创造性。较低的值使结果更确定，较高的值使结果更多样化。"
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
                 

def show_custom_chart_panel():
    """显示自定义图表面板（类似Dash的交互式功能）"""
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    
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
                    (float(df[filter_col].min()), float(df[filter_col].max())),
                    key=f"filter_range_slider_{filter_col}"
                )
                filtered_df = df[(df[filter_col] >= min_val) & (df[filter_col] <= max_val)]
                st.info(f"筛选后数据: {len(filtered_df)} 行 (原始: {len(df)} 行)")
    
    # 生成图表按钮
    if st.button("🎯 生成自定义图表", type="primary"):
        with st.spinner("生成图表中..."):
            try:
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
                    fig = px.histogram(filtered_df, x=x_axis, title=chart_title)
                elif chart_type == "heatmap":
                    # 对于热图，需要先创建透视表
                    pivot_df = filtered_df.pivot_table(index=x_axis, columns=y_axis, aggfunc='size', fill_value=0)
                    fig = px.imshow(pivot_df, title=chart_title)
                
                # 显示图表
                st.plotly_chart(fig, use_container_width=True)
                
                # 提供下载选项
                st.download_button(
                    label="📥 下载图表 (HTML)",
                    data=pio.to_html(fig),
                    file_name=f"chart_{chart_type}_{x_axis}.html",
                    mime="text/html"
                )
                
            except Exception as e:
                st.error(f"生成图表失败: {str(e)}")
                st.info("提示: 请检查所选列的数据类型是否适合所选图表类型。例如，饼图需要分类数据，散点图需要数值数据。")