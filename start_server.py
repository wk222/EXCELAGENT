#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel智能体 MCP 服务器启动脚本

提供多种启动方式和配置选项
"""

import os
import sys
import subprocess

def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   Excel智能体 MCP 服务器                      ║
║              基于Model Context Protocol构建                  ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastmcp
        import pandas
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("💡 请运行: pip install -r requirements_mcp.txt")
        return False

def main():
    """主函数"""
    print_banner()
    
    if not check_dependencies():
        sys.exit(1)
    
    print("请选择启动方式:")
    print("1. HTTP服务器模式 (推荐) - 适合Web集成")
    print("2. STDIO模式 - 适合Claude Desktop等客户端")
    print("3. 开发模式 - 使用MCP Inspector调试")
    print("4. 自定义配置启动")
    print("5. 退出")
    
    while True:
        choice = input("\n请选择 [1-5]: ").strip()
        
        if choice == "1":
            print("\n🌐 启动HTTP服务器模式...")
            cmd = ["python", "excel_mcp_server.py", "--transport", "http"]
            break
        
        elif choice == "2":
            print("\n📍 启动STDIO模式...")
            print("💡 提示: 此模式会等待客户端连接")
            cmd = ["python", "excel_mcp_server.py", "--transport", "stdio"]
            break
        
        elif choice == "3":
            print("\n🔍 启动开发模式 (MCP Inspector)...")
            # 检查是否安装了fastmcp CLI
            try:
                subprocess.run(["fastmcp", "--version"], check=True, 
                             capture_output=True, text=True)
                cmd = ["fastmcp", "dev", "excel_mcp_server.py"]
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("❌ fastmcp CLI未安装，使用普通HTTP模式")
                cmd = ["python", "excel_mcp_server.py", "--transport", "http"]
            break
        
        elif choice == "4":
            print("\n⚙️  自定义配置:")
            transport = input("传输协议 [http/stdio/sse] (默认: http): ").strip() or "http"
            
            if transport in ["http", "sse"]:
                host = input("主机地址 (默认: 127.0.0.1): ").strip() or "127.0.0.1"
                port = input("端口号 (默认: 8080): ").strip() or "8080"
                try:
                    port = int(port)
                except ValueError:
                    port = 8080
                
                cmd = ["python", "excel_mcp_server.py", 
                       "--transport", transport,
                       "--host", host,
                       "--port", str(port)]
            else:
                cmd = ["python", "excel_mcp_server.py", "--transport", transport]
            break
        
        elif choice == "5":
            print("👋 再见!")
            sys.exit(0)
        
        else:
            print("❌ 无效选择，请重新输入")
    
    print(f"\n🚀 执行命令: {' '.join(cmd)}")
    print("按 Ctrl+C 停止服务器\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")

if __name__ == "__main__":
    main() 