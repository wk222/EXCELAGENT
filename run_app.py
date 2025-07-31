#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体Web前端启动脚本

快速启动Excel智能体Web测试界面，包含依赖检查和环境配置
"""

import subprocess
import sys
import os
import time
import platform
import argparse
import webbrowser
from datetime import datetime

# 应用常量
APP_NAME = "Excel智能体"
APP_VERSION = "v2.0"
DEFAULT_PORT = 8501
REQUIREMENTS_FILE = "requirements_mcp.txt"
APP_ENTRY_POINT = "app.py"
LOG_DIR = ".kiro/logs"

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description=f'{APP_NAME} {APP_VERSION} 启动器')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'服务器端口 (默认: {DEFAULT_PORT})')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--check-only', action='store_true', help='仅检查环境，不启动应用')
    return parser.parse_args()

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        print("✅ Streamlit 已安装")
        return True
    except ImportError:
        print("❌ Streamlit 未安装")
        print("💡 正在安装依赖...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE], 
                         check=True)
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return False

def check_environment():
    """检查运行环境"""
    # 检查Python版本
    python_version = platform.python_version()
    print(f"📌 Python版本: {python_version}")
    if sys.version_info < (3, 7):
        print("⚠️ 警告: 推荐使用Python 3.7或更高版本")
    
    # 检查操作系统
    os_name = platform.system()
    os_version = platform.version()
    print(f"📌 操作系统: {os_name} {os_version}")
    
    # 检查文件存在
    if not os.path.exists(APP_ENTRY_POINT):
        print(f"❌ 找不到应用入口文件: {APP_ENTRY_POINT}")
        return False
    
    # 检查设置目录
    settings_dir = ".kiro/settings"
    if not os.path.exists(settings_dir):
        print(f"💡 创建设置目录: {settings_dir}")
        os.makedirs(settings_dir, exist_ok=True)
    
    # 检查日志目录
    if not os.path.exists(LOG_DIR):
        print(f"💡 创建日志目录: {LOG_DIR}")
        os.makedirs(LOG_DIR, exist_ok=True)
    
    return True

def setup_logging(debug=False):
    """设置日志记录"""
    # 确保日志目录存在
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 创建日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"app_{timestamp}.log")
    
    print(f"📝 日志文件: {log_file}")
    
    # 返回日志文件路径
    return log_file

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    print(f"🚀 {APP_NAME} {APP_VERSION} 启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print(f"请手动安装依赖: pip install -r {REQUIREMENTS_FILE}")
        return 1
    
    # 检查环境
    if not check_environment():
        print("环境检查失败，请解决上述问题后重试")
        return 1
    
    # 如果只是检查环境，到此结束
    if args.check_only:
        print("✅ 环境检查完成")
        return 0
    
    # 设置日志
    log_file = setup_logging(args.debug)
    
    # 构建Streamlit命令参数
    streamlit_args = [
        sys.executable, "-m", "streamlit", "run", APP_ENTRY_POINT,
        "--server.port", str(args.port),
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false"
    ]
    
    # 调试模式
    if args.debug:
        streamlit_args.extend(["--logger.level", "debug"])
    
    print(f"🌐 正在启动服务器，端口: {args.port}...")
    print(f"💡 应用地址: http://localhost:{args.port}")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 如果需要自动打开浏览器
    if not args.no_browser:
        # 延迟2秒后打开浏览器，给服务器启动留出时间
        def open_browser():
            time.sleep(2)
            webbrowser.open(f"http://localhost:{args.port}")
        
        import threading
        threading.Thread(target=open_browser).start()
    
    try:
        # 启动Streamlit应用，将输出重定向到日志文件
        with open(log_file, "w") as log:
            process = subprocess.Popen(
                streamlit_args,
                stdout=log if not args.debug else None,
                stderr=log if not args.debug else None
            )
            process.wait()
    except KeyboardInterrupt:
        print("\n👋 Web前端已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())