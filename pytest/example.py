#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python WebSocket客户端使用示例
演示如何使用WebSocket客户端进行连接、发送消息和处理事件
"""

import asyncio
import json
import logging
import time
from websocket_client import WebSocketClient, WebSocketManager, create_websocket_client


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


async def basic_example():
    """基本使用示例"""
    print("🚀 基本WebSocket客户端示例")
    print("=" * 50)
    
    # 创建WebSocket客户端
    client = WebSocketClient()
    
    # 配置请求头（仅在握手阶段有效）
    headers = {
        'Authorization': 'Bearer python-test-token-123',
        'X-Client-Version': '1.0.0',
        'X-User-Agent': 'Python-WebSocket-Client',
        'X-API-Key': 'python-api-key-456',
        'X-Session-ID': f'session-{int(time.time())}',
        'Origin': 'https://python-client.com'
    }
    
    # 设置事件处理器
    @client.on_message
    async def handle_message(message):
        print(f"📨 收到服务器消息: {message}")
        
        # 如果是JSON消息，可以进行特殊处理
        if isinstance(message, dict):
            print(f"📋 JSON消息类型: {message.get('type', '未知')}")
    
    @client.on_error
    async def handle_error(error):
        print(f"❌ WebSocket发生错误: {error}")
    
    @client.on_connect
    async def handle_connect():
        print("✅ WebSocket连接成功建立")
    
    @client.on_disconnect
    async def handle_disconnect(reason):
        print(f"🔌 WebSocket连接已断开: {reason}")
    
    try:
        # 连接到WebSocket服务器
        # 注意：这里使用测试服务器，您需要替换为实际的服务器地址
        url = 'wss://echo.websocket.org'  # WebSocket回声测试服务器
        
        print(f"🌐 正在连接到: {url}")
        print(f"📤 请求头信息: {json.dumps(headers, indent=2, ensure_ascii=False)}")
        
        success = await client.connect(url, headers=headers)
        
        if not success:
            print("❌ 连接失败")
            return
        
        # 发送测试消息
        print("\n📤 发送测试消息...")
        
        # 1. 发送简单文本消息
        await client.send("Hello, WebSocket Server from Python!")
        
        # 等待1秒
        await asyncio.sleep(1)
        
        # 2. 发送JSON消息
        json_message = {
            "type": "greeting",
            "data": {
                "message": "你好，这是来自Python的JSON消息",
                "timestamp": time.time(),
                "client_info": {
                    "language": "Python",
                    "version": "3.x",
                    "library": "websockets"
                }
            }
        }
        await client.send(json_message)
        
        # 等待2秒
        await asyncio.sleep(2)
        
        # 3. 发送心跳检测
        print("💓 发送心跳检测...")
        ping_success = await client.ping(b'Python heartbeat')
        if ping_success:
            print("✅ 心跳检测成功")
        else:
            print("❌ 心跳检测失败")
        
        # 等待3秒观察消息
        await asyncio.sleep(3)
        
        # 4. 发送定期消息
        for i in range(3):
            periodic_message = {
                "type": "periodic",
                "sequence": i + 1,
                "message": f"定期消息 #{i + 1}",
                "timestamp": time.time()
            }
            await client.send(periodic_message)
            await asyncio.sleep(1)
        
        print("\n📊 连接状态:", client.get_connection_state())
        print("🔗 连接是否打开:", client.is_connection_open())
        
    except KeyboardInterrupt:
        print("\n⚠️ 收到中断信号，正在关闭连接...")
    except Exception as e:
        print(f"❌ 发生异常: {e}")
    finally:
        # 关闭连接
        if client.is_connection_open():
            await client.close(1000, "示例演示完成")
        print("👋 示例结束")


async def advanced_example():
    """高级使用示例：自定义客户端类"""
    print("\n🔧 高级WebSocket客户端示例")
    print("=" * 50)
    
    class CustomWebSocketClient(WebSocketClient):
        """自定义WebSocket客户端类"""
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.message_history = []
            self.is_authenticated = False
            self.auth_token = None
        
        async def authenticate(self, token: str):
            """发送认证消息"""
            self.auth_token = token
            auth_message = {
                "type": "authenticate",
                "token": token,
                "timestamp": time.time()
            }
            await self.send(auth_message)
            self.logger.info(f"已发送认证消息: {token}")
        
        async def _handle_message(self, message):
            """重写消息处理方法"""
            # 保存消息到历史记录
            self.message_history.append({
                "message": message,
                "timestamp": time.time(),
                "received_at": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # 处理认证响应
            if isinstance(message, dict) and message.get('type') == 'auth_response':
                if message.get('success'):
                    self.is_authenticated = True
                    self.logger.info("✅ 认证成功")
                else:
                    self.logger.error(f"❌ 认证失败: {message.get('error', '未知错误')}")
            
            # 调用父类方法
            await super()._handle_message(message)
        
        def get_message_history(self):
            """获取消息历史"""
            return self.message_history
        
        def get_stats(self):
            """获取客户端统计信息"""
            return {
                "total_messages": len(self.message_history),
                "is_authenticated": self.is_authenticated,
                "connection_state": self.get_connection_state(),
                "auth_token": self.auth_token
            }
    
    # 创建自定义客户端
    custom_client = CustomWebSocketClient()
    
    # 设置事件处理器
    @custom_client.on_message
    async def handle_custom_message(message):
        print(f"🎯 自定义客户端收到消息: {message}")
    
    @custom_client.on_connect
    async def handle_custom_connect():
        print("🔗 自定义客户端连接成功")
        # 连接成功后立即认证
        await custom_client.authenticate("custom-python-token-789")
    
    try:
        # 连接到服务器
        headers = {
            'Authorization': 'Bearer custom-token',
            'X-Client-Type': 'CustomPythonClient',
            'X-Features': 'auth,history,stats'
        }
        
        await custom_client.connect('wss://echo.websocket.org', headers=headers)
        
        # 发送一些测试消息
        for i in range(3):
            test_message = {
                "type": "test_message",
                "id": i + 1,
                "content": f"自定义客户端测试消息 {i + 1}",
                "features": ["history", "stats", "auth"]
            }
            await custom_client.send(test_message)
            await asyncio.sleep(1)
        
        # 等待消息处理
        await asyncio.sleep(2)
        
        # 显示统计信息
        stats = custom_client.get_stats()
        print(f"\n📈 客户端统计信息:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        # 显示消息历史
        history = custom_client.get_message_history()
        print(f"\n📝 消息历史 (共{len(history)}条):")
        for i, record in enumerate(history[-3:], 1):  # 显示最后3条
            print(f"  {i}. [{record['received_at']}] {record['message']}")
        
    except Exception as e:
        print(f"❌ 自定义客户端示例发生错误: {e}")
    finally:
        await custom_client.close()


async def manager_example():
    """WebSocket管理器示例"""
    print("\n🏢 WebSocket管理器示例")
    print("=" * 50)
    
    # 创建WebSocket管理器
    manager = WebSocketManager()
    
    # 创建多个客户端
    client1 = manager.create_client("echo_client")
    client2 = manager.create_client("test_client")
    
    # 配置客户端1
    @client1.on_message
    async def handle_echo_message(message):
        print(f"🔄 Echo客户端收到: {message}")
    
    # 配置客户端2
    @client2.on_message
    async def handle_test_message(message):
        print(f"🧪 Test客户端收到: {message}")
    
    try:
        # 分别连接客户端
        headers1 = {'X-Client-Name': 'EchoClient'}
        headers2 = {'X-Client-Name': 'TestClient'}
        
        await client1.connect('wss://echo.websocket.org', headers=headers1)
        await client2.connect('wss://echo.websocket.org', headers=headers2)
        
        # 查看所有客户端状态
        print("\n📋 客户端状态:")
        for name, state in manager.list_clients().items():
            print(f"  {name}: {state}")
        
        # 通过不同客户端发送消息
        await client1.send("来自Echo客户端的消息")
        await client2.send("来自Test客户端的消息")
        
        # 等待消息处理
        await asyncio.sleep(2)
        
        # 批量发送消息
        messages = [
            "批量消息 1",
            "批量消息 2", 
            "批量消息 3"
        ]
        
        for msg in messages:
            await client1.send(f"Echo: {msg}")
            await client2.send(f"Test: {msg}")
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"❌ 管理器示例发生错误: {e}")
    finally:
        # 关闭所有连接
        await manager.close_all()
        print("🔒 所有连接已关闭")


async def convenience_function_example():
    """便捷函数示例"""
    print("\n⚡ 便捷函数示例")
    print("=" * 50)
    
    # 使用便捷函数创建客户端
    headers = {
        'Authorization': 'Bearer convenience-token',
        'X-Usage': 'ConvenienceFunction'
    }
    
    try:
        client = await create_websocket_client(
            'wss://echo.websocket.org',
            headers=headers
        )
        
        # 设置消息处理器
        @client.on_message
        async def handle_convenience_message(message):
            print(f"⚡ 便捷客户端收到: {message}")
        
        # 发送消息
        await client.send("这是通过便捷函数创建的客户端发送的消息")
        
        # 等待响应
        await asyncio.sleep(2)
        
        await client.close()
        
    except Exception as e:
        print(f"❌ 便捷函数示例发生错误: {e}")


async def main():
    """主函数：运行所有示例"""
    print("🐍 Python WebSocket客户端完整示例")
    print("=" * 60)
    
    try:
        # 运行所有示例
        await basic_example()
        await advanced_example()
        await manager_example()
        await convenience_function_example()
        
    except KeyboardInterrupt:
        print("\n⚠️ 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
    finally:
        print("\n🎉 所有示例执行完成！")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
