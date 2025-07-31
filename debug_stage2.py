#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试阶段二结果的脚本
"""

import streamlit as st

def debug_stage2_result():
    """调试阶段二结果"""
    st.write("## 🔍 阶段二结果调试")
    
    if 'stage2_result' in st.session_state:
        result = st.session_state.stage2_result
        st.write(f"**Status:** {result.status}")
        st.write(f"**Message:** {result.message}")
        st.write(f"**Data exists:** {result.data is not None}")
        st.write(f"**Error:** {result.error}")
        
        if result.data:
            st.write("**Data keys:**", list(result.data.keys()))
            
            exec_results = result.data.get('execution_results', {})
            st.write("**Execution results keys:**", list(exec_results.keys()))
            
            # 检查图表
            charts = exec_results.get('plotly_figures', [])
            st.write(f"**Charts count:** {len(charts)}")
            
            if charts:
                st.write("**Chart types:**")
                for i, chart in enumerate(charts):
                    st.write(f"  Chart {i+1}: {type(chart)} - Length: {len(str(chart)) if chart else 0}")
            
            # 检查其他输出
            stdout = exec_results.get('stdout', '')
            stderr = exec_results.get('stderr', '')
            st.write(f"**STDOUT length:** {len(stdout)}")
            st.write(f"**STDERR length:** {len(stderr)}")
            
            if stdout:
                st.write("**STDOUT:**")
                st.text(stdout[:500] + "..." if len(stdout) > 500 else stdout)
    else:
        st.write("❌ stage2_result 不存在在 session_state 中")

if __name__ == "__main__":
    debug_stage2_result() 