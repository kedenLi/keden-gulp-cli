#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python WebSocket客户端安装和设置脚本
"""

import subprocess
import sys
import os


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version}")
    return True


def install_dependencies():
    """安装依赖包"""
    print("📦 正在安装依赖包...")
    
    try:
        # 升级pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # 安装基础依赖
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets>=11.0.3"])
        
        # 如果存在requirements.txt，安装完整依赖
        if os.path.exists("requirements.txt"):
            print("📋 发现requirements.txt，安装完整依赖...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ 依赖包安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装依赖包失败: {e}")
        return False


def run_test():
    """运行测试"""
    print("🧪 运行基本测试...")
    
    try:
        # 导入测试
        import websockets
        from websocket_client import WebSocketClient
        
        print("✅ 模块导入测试通过")
        
        # 运行简单测试
        print("🔗 运行连接测试...")
        import asyncio
        
        async def test_connection():
            client = WebSocketClient()
            print("WebSocket客户端创建成功")
            print(f"连接状态: {client.get_connection_state()}")
            return True
        
        result = asyncio.run(test_connection())
        if result:
            print("✅ 基本功能测试通过")
            return True
        else:
            print("❌ 基本功能测试失败")
            return False
            
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def show_usage():
    """显示使用说明"""
    print("\n" + "="*50)
    print("🎉 安装完成！可以开始使用WebSocket客户端了")
    print("="*50)
    print()
    print("📚 快速开始:")
    print("   python test_websocket.py    # 运行简单测试")
    print("   python example.py           # 运行完整示例")
    print()
    print("📖 文档:")
    print("   README.md                   # 详细使用文档")
    print()
    print("🔧 基本用法:")
    print("""
from websocket_client import WebSocketClient
import asyncio

async def main():
    client = WebSocketClient()
    await client.connect('wss://echo.websocket.org')
    await client.send('Hello!')
    await asyncio.sleep(2)
    await client.close()

asyncio.run(main())
""")


def main():
    """主函数"""
    print("🐍 Python WebSocket客户端安装程序")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 安装失败，请检查网络连接和权限")
        sys.exit(1)
    
    # 运行测试
    if not run_test():
        print("⚠️ 测试失败，但安装可能已完成")
        print("请手动检查依赖是否正确安装")
    
    # 显示使用说明
    show_usage()


if __name__ == "__main__":
    main()
