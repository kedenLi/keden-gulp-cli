#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的WebSocket测试脚本
用于快速测试WebSocket连接和消息发送
"""

import asyncio
import time
from websocket_client import WebSocketClient


async def simple_test():
    """简单的WebSocket连接测试"""
    print("🧪 WebSocket连接测试开始...")
    
    client = WebSocketClient()
    
    # 配置请求头
    headers = {
        'Authorization': 'Bearer simple-test-token',
        'X-Client-Type': 'Simple-Test-Client',
        'X-Test-ID': f'test-{int(time.time())}'
    }
    
    # 设置简单的消息处理器
    @client.on_message
    async def handle_message(message):
        print(f"📨 收到回应: {message}")
    
    @client.on_connect
    async def handle_connect():
        print("✅ 连接成功建立")
    
    @client.on_error
    async def handle_error(error):
        print(f"❌ 发生错误: {error}")
    
    try:
        # 连接到测试服务器
        print("🔗 正在连接到WebSocket测试服务器...")
        success = await client.connect('wss://echo.websocket.org', headers=headers)
        
        if not success:
            print("❌ 连接失败")
            return
        
        # 发送测试消息
        print("📤 发送测试消息...")
        await client.send(f"这是一个测试消息：{time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 发送JSON消息
        json_msg = {
            "type": "test",
            "content": "这是JSON格式的测试消息",
            "timestamp": time.time(),
            "test_id": "simple_test_001"
        }
        await client.send(json_msg)
        
        # 等待3秒查看响应
        await asyncio.sleep(3)
        
        # 测试心跳
        print("💓 测试心跳...")
        ping_result = await client.ping(b'test-ping')
        if ping_result:
            print("✅ 心跳测试成功")
        else:
            print("❌ 心跳测试失败")
        
        print(f"🔍 连接状态: {client.get_connection_state()}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        print("🔒 关闭连接...")
        await client.close()
        print("✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(simple_test())
