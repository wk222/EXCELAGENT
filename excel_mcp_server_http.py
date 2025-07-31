#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体 MCP HTTP 服务器

为JavaScript前端提供HTTP API接口的MCP服务器版本
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import traceback

# 导入现有的MCP服务器功能
from excel_mcp_server import (
    analyze_excel_data_core,
    generate_visualizations_only_core,
    get_data_summary_core,
    execute_custom_code_core,
    generate_deep_analysis_core
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'Excel智能体 MCP HTTP服务器',
        'version': '2.0'
    })

@app.route('/tools/analyze_excel_data', methods=['POST'])
def api_analyze_excel_data():
    """完整的Excel数据分析API"""
    try:
        data = request.get_json()
        
        if not data or 'file_data' not in data or 'question' not in data:
            return jsonify({
                'status': '失败',
                'message': '缺少必要参数',
                'error': '需要提供file_data和question参数'
            }), 400
        
        file_data = data['file_data']
        question = data['question']
        
        logger.info(f"收到分析请求: {question}")
        
        # 调用核心分析函数
        result = analyze_excel_data_core(file_data, question)
        
        return jsonify(result.dict())
        
    except Exception as e:
        logger.error(f"分析请求处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': '失败',
            'message': '服务器内部错误',
            'error': str(e)
        }), 500

@app.route('/tools/get_data_summary', methods=['POST'])
def api_get_data_summary():
    """获取数据摘要API"""
    try:
        data = request.get_json()
        
        if not data or 'file_data' not in data:
            return jsonify({
                'status': '失败',
                'message': '缺少必要参数',
                'error': '需要提供file_data参数'
            }), 400
        
        file_data = data['file_data']
        
        logger.info("收到数据摘要请求")
        
        # 调用核心摘要函数
        result = get_data_summary_core(file_data)
        
        return jsonify(result.dict())
        
    except Exception as e:
        logger.error(f"数据摘要请求处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': '失败',
            'message': '服务器内部错误',
            'error': str(e)
        }), 500

@app.route('/tools/generate_visualizations_only', methods=['POST'])
def api_generate_visualizations():
    """仅生成可视化API"""
    try:
        data = request.get_json()
        
        if not data or 'file_data' not in data:
            return jsonify({
                'status': '失败',
                'message': '缺少必要参数',
                'error': '需要提供file_data参数'
            }), 400
        
        file_data = data['file_data']
        chart_type = data.get('chart_type', 'auto')
        
        logger.info(f"收到可视化请求: {chart_type}")
        
        # 调用核心可视化函数
        result = generate_visualizations_only_core(file_data, chart_type)
        
        # 转换结果格式以匹配AnalysisResult
        analysis_result = {
            'status': result.status,
            'message': result.message,
            'data': {
                'charts': result.charts if result.status == '成功' else []
            }
        }
        
        if result.status != '成功':
            analysis_result['error'] = result.error
        
        return jsonify(analysis_result)
        
    except Exception as e:
        logger.error(f"可视化请求处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': '失败',
            'message': '服务器内部错误',
            'error': str(e)
        }), 500

@app.route('/tools/execute_custom_code', methods=['POST'])
def api_execute_custom_code():
    """执行自定义代码API"""
    try:
        data = request.get_json()
        
        if not data or 'file_data' not in data or 'python_code' not in data:
            return jsonify({
                'status': '失败',
                'message': '缺少必要参数',
                'error': '需要提供file_data和python_code参数'
            }), 400
        
        file_data = data['file_data']
        python_code = data['python_code']
        
        logger.info("收到自定义代码执行请求")
        
        # 调用核心代码执行函数
        result = execute_custom_code_core(file_data, python_code)
        
        return jsonify(result.dict())
        
    except Exception as e:
        logger.error(f"代码执行请求处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': '失败',
            'message': '服务器内部错误',
            'error': str(e)
        }), 500

@app.route('/tools/generate_deep_analysis', methods=['POST'])
def api_generate_deep_analysis():
    """生成深度分析API"""
    try:
        data = request.get_json()
        
        required_params = ['stage2_question', 'stage3_question', 'stage2_result']
        for param in required_params:
            if param not in data:
                return jsonify({
                    'status': '失败',
                    'message': '缺少必要参数',
                    'error': f'需要提供{param}参数'
                }), 400
        
        stage2_question = data['stage2_question']
        stage3_question = data['stage3_question']
        stage2_result_dict = data['stage2_result']
        data_summary = data.get('data_summary', '')
        
        logger.info(f"收到深度分析请求: {stage3_question}")
        
        # 将字典转换为AnalysisResult对象
        from excel_mcp_server import AnalysisResult
        stage2_result = AnalysisResult(**stage2_result_dict)
        
        # 调用核心深度分析函数
        result = generate_deep_analysis_core(
            stage2_question=stage2_question,
            stage3_question=stage3_question,
            stage2_result=stage2_result,
            data_summary=data_summary
        )
        
        return jsonify(result.dict())
        
    except Exception as e:
        logger.error(f"深度分析请求处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': '失败',
            'message': '服务器内部错误',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': '失败',
        'message': '接口不存在',
        'error': '404 Not Found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': '失败',
        'message': '服务器内部错误',
        'error': '500 Internal Server Error'
    }), 500

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Excel智能体 MCP HTTP服务器')
    parser.add_argument('--host', default='127.0.0.1', help='服务器地址')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    print("🚀 启动Excel智能体 MCP HTTP服务器")
    print(f"📡 服务地址: http://{args.host}:{args.port}")
    print("🔧 可用接口:")
    print("  GET  /health - 健康检查")
    print("  POST /tools/analyze_excel_data - 完整分析")
    print("  POST /tools/get_data_summary - 数据摘要") 
    print("  POST /tools/generate_visualizations_only - 仅生成图表")
    print("  POST /tools/execute_custom_code - 执行自定义代码")
    print("  POST /tools/generate_deep_analysis - 深度分析")
    print("\n💡 前端连接地址:", f"http://{args.host}:{args.port}")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )