#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端 - 自定义图表页面

提供高级自定义图表创建功能
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

def render():
    """渲染自定义图表页面"""
    # 主标题
    st.markdown('<h1 class="main-header">📈 Excel智能体 - 自定义图表</h1>', unsafe_allow_html=True)
    
    if st.session_state.uploaded_file_data is None:
        st.warning("⚠️ 请先上传Excel文件")
        if st.button("返回上传页面"):
            st.session_state.sidebar_selection = "首页"
            st.rerun()
        return
    
    # 显示当前分析的文件信息
    file_data = st.session_state.uploaded_file_data
    st.info(f"📄 当前分析文件: **{file_data['filename']}** | 工作表: **{file_data['current_sheet']}** | 数据: {file_data['shape'][0]} 行 × {file_data['shape'][1]} 列")
    
    # 重建DataFrame
    df = pd.DataFrame(file_data['dataframe'])
    
    if df.empty:
        st.warning("⚠️ 数据为空")
        return
    
    # 创建两列布局
    left_col, right_col = st.columns([1, 1.5])
    
    with left_col:
        st.markdown("### 🔧 图表配置")
        
        # 图表类型选择
        chart_type = st.selectbox(
            "📊 图表类型",
            ["bar", "line", "scatter", "pie", "box", "violin", "histogram", "heatmap", "area", "bubble", "sunburst", "treemap"],
            help="选择要生成的图表类型"
        )
        
        # 根据图表类型显示不同的配置选项
        if chart_type in ["sunburst", "treemap"]:
            # 层次结构图表
            path_cols = st.multiselect(
                "选择层次路径列",
                df.columns.tolist(),
                help="按层次顺序选择分类列"
            )
            
            value_col = st.selectbox(
                "数值列",
                ["无"] + [col for col in df.columns if df[col].dtype in ['int64', 'float64']],
                help="选择用于计算大小的数值列"
            )
            if value_col == "无":
                value_col = None
                
        elif chart_type in ["pie"]:
            # 饼图
            names_col = st.selectbox(
                "名称列",
                df.columns.tolist(),
                help="选择用于分类的列"
            )
            
            values_col = st.selectbox(
                "数值列",
                [col for col in df.columns if df[col].dtype in ['int64', 'float64']],
                help="选择用于计算大小的数值列"
            )
            
        else:
            # 常规图表
            x_axis = st.selectbox(
                "📐 X轴",
                df.columns.tolist(),
                help="选择X轴数据列"
            )
            
            if chart_type not in ["histogram"]:
                y_axis = st.selectbox(
                    "📏 Y轴", 
                    df.columns.tolist(),
                    index=1 if len(df.columns) > 1 else 0,
                    help="选择Y轴数据列"
                )
            else:
                y_axis = None
        
        # 高级选项
        with st.expander("🔧 高级选项", expanded=True):
            # 图表标题
            chart_title = st.text_input(
                "📝 图表标题",
                value=f"{chart_type.title()} Chart",
                help="自定义图表标题"
            )
            
            # 颜色主题
            color_theme = st.selectbox(
                "🎨 颜色主题",
                ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"],
                help="选择图表颜色主题"
            )
            
            if chart_type not in ["sunburst", "treemap", "pie"]:
                # 颜色分组
                color_column = st.selectbox(
                    "🎨 颜色分组 (可选)",
                    ["无"] + df.columns.tolist(),
                    help="根据此列的值进行颜色分组"
                )
                if color_column == "无":
                    color_column = None
                
                # 尺寸映射（仅对scatter和bubble图有效）
                if chart_type in ["scatter", "bubble"]:
                    size_column = st.selectbox(
                        "⭕ 点大小映射 (可选)",
                        ["无"] + [col for col in df.columns if df[col].dtype in ['int64', 'float64']],
                        help="根据此列的值调整点的大小"
                    )
                    if size_column == "无":
                        size_column = None
                else:
                    size_column = None
            
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
                
                # 分类筛选
                categorical_cols = df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    cat_filter_col = st.selectbox("分类筛选列", ["无"] + list(categorical_cols))
                    if cat_filter_col != "无":
                        unique_values = df[cat_filter_col].unique().tolist()
                        selected_values = st.multiselect(
                            f"选择 {cat_filter_col} 的值",
                            unique_values,
                            default=unique_values[:5] if len(unique_values) > 5 else unique_values
                        )
                        if selected_values:
                            filtered_df = filtered_df[filtered_df[cat_filter_col].isin(selected_values)]
                            st.info(f"筛选后数据: {len(filtered_df)} 行")
        
        # 生成图表按钮
        generate_chart = st.button("🎯 生成自定义图表", type="primary")
    
    with right_col:
        st.markdown("### 📊 图表预览")
        
        if generate_chart:
            with st.spinner("生成图表中..."):
                try:
                    # 设置主题
                    if color_theme != "none":
                        template = color_theme
                    else:
                        template = "plotly"
                    
                    # 根据图表类型生成对应图表
                    if chart_type == "bar":
                        fig = px.bar(filtered_df, x=x_axis, y=y_axis, color=color_column, 
                                    title=chart_title, template=template)
                    
                    elif chart_type == "line":
                        fig = px.line(filtered_df, x=x_axis, y=y_axis, color=color_column, 
                                     title=chart_title, template=template)
                    
                    elif chart_type == "scatter":
                        fig = px.scatter(filtered_df, x=x_axis, y=y_axis, color=color_column, 
                                        size=size_column, title=chart_title, template=template)
                    
                    elif chart_type == "bubble":
                        fig = px.scatter(filtered_df, x=x_axis, y=y_axis, color=color_column, 
                                        size=size_column, title=chart_title, template=template,
                                        size_max=30)
                    
                    elif chart_type == "pie":
                        fig = px.pie(filtered_df, names=names_col, values=values_col, 
                                    title=chart_title, template=template)
                    
                    elif chart_type == "box":
                        fig = px.box(filtered_df, x=x_axis, y=y_axis, color=color_column, 
                                    title=chart_title, template=template)
                    
                    elif chart_type == "violin":
                        fig = px.violin(filtered_df, x=x_axis, y=y_axis, color=color_column, 
                                       title=chart_title, template=template)
                    
                    elif chart_type == "histogram":
                        fig = px.histogram(filtered_df, x=x_axis, color=color_column, 
                                          title=chart_title, template=template)
                    
                    elif chart_type == "heatmap":
                        # 对于热图，需要先创建透视表
                        pivot_df = filtered_df.pivot_table(index=x_axis, columns=y_axis, aggfunc='size', fill_value=0)
                        fig = px.imshow(pivot_df, title=chart_title, template=template)
                    
                    elif chart_type == "area":
                        fig = px.area(filtered_df, x=x_axis, y=y_axis, color=color_column, 
                                     title=chart_title, template=template)
                    
                    elif chart_type == "sunburst":
                        fig = px.sunburst(filtered_df, path=path_cols, values=value_col, 
                                         title=chart_title, template=template)
                    
                    elif chart_type == "treemap":
                        fig = px.treemap(filtered_df, path=path_cols, values=value_col, 
                                        title=chart_title, template=template)
                    
                    # 显示图表
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 提供下载选项
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 下载图表 (HTML)",
                            data=pio.to_html(fig),
                            file_name=f"chart_{chart_type}.html",
                            mime="text/html"
                        )
                    
                    with col2:
                        # 保存图表到session state以便后续使用
                        if 'custom_charts' not in st.session_state:
                            st.session_state.custom_charts = []
                        
                        chart_data = {
                            'type': chart_type,
                            'title': chart_title,
                            'json': pio.to_json(fig)
                        }
                        
                        if st.button("💾 保存到我的图表"):
                            st.session_state.custom_charts.append(chart_data)
                            st.success("图表已保存！")
                    
                except Exception as e:
                    st.error(f"生成图表失败: {str(e)}")
                    st.info("提示: 请检查所选列的数据类型是否适合所选图表类型。例如，饼图需要分类数据，散点图需要数值数据。")
        
        else:
            # 显示图表预览占位符
            st.info("👈 请配置图表参数并点击生成按钮")
            
            # 如果有保存的图表，显示最近保存的图表
            if 'custom_charts' in st.session_state and st.session_state.custom_charts:
                st.markdown("### 🔍 最近保存的图表")
                
                # 显示最近保存的图表
                recent_chart = st.session_state.custom_charts[-1]
                st.markdown(f"**{recent_chart['title']}** ({recent_chart['type']})")
                
                try:
                    fig = pio.from_json(recent_chart['json'])
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"加载图表失败: {str(e)}")
    
    # 我的图表库
    if 'custom_charts' in st.session_state and st.session_state.custom_charts:
        st.markdown("---")
        st.markdown("## 📚 我的图表库")
        
        # 创建选项卡，每个选项卡显示一个保存的图表
        tabs = st.tabs([f"图表 {i+1}: {chart['title']}" for i, chart in enumerate(st.session_state.custom_charts)])
        
        for i, tab in enumerate(tabs):
            with tab:
                chart = st.session_state.custom_charts[i]
                st.markdown(f"**类型:** {chart['type']}")
                
                try:
                    fig = pio.from_json(chart['json'])
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 下载按钮
                    st.download_button(
                        label="📥 下载图表 (HTML)",
                        data=pio.to_html(fig),
                        file_name=f"chart_{i+1}_{chart['type']}.html",
                        mime="text/html"
                    )
                    
                    # 删除按钮
                    if st.button(f"🗑️ 删除图表", key=f"delete_{i}"):
                        st.session_state.custom_charts.pop(i)
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"加载图表失败: {str(e)}")
    
    # 数据预览
    st.markdown("---")
    with st.expander("👀 数据预览", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)