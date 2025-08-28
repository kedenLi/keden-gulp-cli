#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python WebSocket客户端封装类
支持自定义请求头、自动重连、心跳检测等功能
"""

import asyncio
import json
import logging
import ssl
import time
from typing import Dict, Optional, Callable, Any, Union
from urllib.parse import urlparse

try:
    import websockets
    from websockets.exceptions import ConnectionClosed, WebSocketException
except ImportError:
    print("请安装websockets库: pip install websockets")
    raise


class WebSocketClient:
    """
    Python WebSocket客户端类
    
    功能特性:
    - 支持自定义请求头（握手阶段）
    - 自动重连机制
    - 心跳检测
    - JSON消息支持
    - 异步事件处理
    - SSL/TLS支持
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化WebSocket客户端
        
        Args:
            logger: 可选的日志记录器
        """
        self.websocket = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_interval = 3.0  # 重连间隔（秒）
        self.ping_interval = 30.0      # 心跳间隔（秒）
        self.ping_timeout = 10.0       # 心跳超时（秒）
        
        # 连接参数存储，用于重连
        self._url = None
        self._headers = None
        self._ssl_context = None
        
        # 事件处理器
        self.on_message_handler: Optional[Callable] = None
        self.on_error_handler: Optional[Callable] = None
        self.on_connect_handler: Optional[Callable] = None
        self.on_disconnect_handler: Optional[Callable] = None
        
        # 日志配置
        self.logger = logger or self._setup_logger()
        
        # 任务管理
        self._tasks = set()
        self._ping_task = None
        
    def _setup_logger(self) -> logging.Logger:
        """设置默认日志记录器"""
        logger = logging.getLogger('WebSocketClient')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def connect(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        ssl_context: Optional[ssl.SSLContext] = None,
        **kwargs
    ) -> bool:
        """
        连接到WebSocket服务器
        
        Args:
            url: WebSocket服务器地址
            headers: 自定义请求头（仅在握手阶段有效）
            ssl_context: SSL上下文（用于wss连接）
            **kwargs: 其他连接参数
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 存储连接参数用于重连
            self._url = url
            self._headers = headers or {}
            self._ssl_context = ssl_context
            
            # 默认请求头
            default_headers = {
                'User-Agent': 'Python WebSocket Client/1.0',
                'Accept': '*/*'
            }
            
            # 合并请求头
            final_headers = {**default_headers, **self._headers}
            
            self.logger.info(f"正在连接到WebSocket服务器: {url}")
            self.logger.info(f"请求头信息: {final_headers}")
            
            # 配置连接参数
            connect_kwargs = {
                'extra_headers': final_headers,
                'ping_interval': self.ping_interval,
                'ping_timeout': self.ping_timeout,
                **kwargs
            }
            
            # 处理SSL连接
            parsed_url = urlparse(url)
            if parsed_url.scheme == 'wss':
                if ssl_context is None:
                    ssl_context = ssl.create_default_context()
                connect_kwargs['ssl'] = ssl_context
            
            # 建立WebSocket连接
            self.websocket = await websockets.connect(url, **connect_kwargs)
            
            self.is_connected = True
            self.reconnect_attempts = 0
            
            self.logger.info("WebSocket连接成功建立")
            
            # 触发连接事件
            if self.on_connect_handler:
                await self._safe_call_handler(self.on_connect_handler)
            
            # 启动消息监听任务
            task = asyncio.create_task(self._message_listener())
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
            
            return True
            
        except Exception as e:
            self.logger.error(f"WebSocket连接失败: {e}")
            if self.on_error_handler:
                await self._safe_call_handler(self.on_error_handler, e)
            return False
    
    async def _message_listener(self):
        """消息监听器"""
        try:
            async for message in self.websocket:
                try:
                    # 尝试解析JSON消息
                    try:
                        data = json.loads(message)
                        await self._handle_message(data)
                    except json.JSONDecodeError:
                        # 如果不是JSON，直接处理原始消息
                        await self._handle_message(message)
                        
                except Exception as e:
                    self.logger.error(f"处理消息时发生错误: {e}")
                    
        except ConnectionClosed as e:
            self.logger.warning(f"WebSocket连接已关闭: {e}")
            self.is_connected = False
            
            # 触发断开连接事件
            if self.on_disconnect_handler:
                await self._safe_call_handler(self.on_disconnect_handler, e)
            
            # 尝试重连
            if self.reconnect_attempts < self.max_reconnect_attempts:
                await self._attempt_reconnect()
                
        except Exception as e:
            self.logger.error(f"消息监听器发生错误: {e}")
            self.is_connected = False
            
            if self.on_error_handler:
                await self._safe_call_handler(self.on_error_handler, e)
    
    async def _handle_message(self, message: Union[str, dict]):
        """处理接收到的消息"""
        self.logger.info(f"收到消息: {message}")
        
        if self.on_message_handler:
            await self._safe_call_handler(self.on_message_handler, message)
    
    async def _safe_call_handler(self, handler: Callable, *args):
        """安全调用事件处理器"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(*args)
            else:
                handler(*args)
        except Exception as e:
            self.logger.error(f"调用事件处理器时发生错误: {e}")
    
    async def _attempt_reconnect(self):
        """尝试重连"""
        self.reconnect_attempts += 1
        self.logger.info(f"尝试重连... ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        await asyncio.sleep(self.reconnect_interval)
        
        if self._url:
            success = await self.connect(
                self._url,
                headers=self._headers,
                ssl_context=self._ssl_context
            )
            if not success:
                self.logger.error("重连失败")
    
    async def send(self, message: Union[str, dict]) -> bool:
        """
        发送消息到WebSocket服务器
        
        Args:
            message: 要发送的消息（字符串或字典）
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_connected or not self.websocket:
            self.logger.error("WebSocket未连接，无法发送消息")
            return False
        
        try:
            # 如果是字典，转换为JSON字符串
            if isinstance(message, dict):
                data = json.dumps(message, ensure_ascii=False)
            else:
                data = str(message)
            
            await self.websocket.send(data)
            self.logger.info(f"消息已发送: {data}")
            return True
            
        except Exception as e:
            self.logger.error(f"发送消息时发生错误: {e}")
            return False
    
    async def ping(self, data: bytes = b'ping') -> bool:
        """
        发送Ping消息进行心跳检测
        
        Args:
            data: Ping数据
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_connected or not self.websocket:
            return False
        
        try:
            pong_waiter = await self.websocket.ping(data)
            await asyncio.wait_for(pong_waiter, timeout=self.ping_timeout)
            self.logger.debug(f"心跳检测成功: {data}")
            return True
        except Exception as e:
            self.logger.error(f"心跳检测失败: {e}")
            return False
    
    async def close(self, code: int = 1000, reason: str = "正常关闭"):
        """
        关闭WebSocket连接
        
        Args:
            code: 关闭代码
            reason: 关闭原因
        """
        if self.websocket:
            self.is_connected = False
            
            # 取消所有任务
            for task in self._tasks:
                if not task.done():
                    task.cancel()
            
            if self._ping_task and not self._ping_task.done():
                self._ping_task.cancel()
            
            # 关闭连接
            await self.websocket.close(code, reason)
            self.logger.info(f"WebSocket连接已关闭: {reason}")
    
    def is_connection_open(self) -> bool:
        """
        检查连接是否打开
        
        Returns:
            bool: 连接是否打开
        """
        return self.is_connected and self.websocket and not self.websocket.closed
    
    def get_connection_state(self) -> str:
        """
        获取连接状态
        
        Returns:
            str: 连接状态描述
        """
        if not self.websocket:
            return 'DISCONNECTED'
        
        if self.websocket.closed:
            return 'CLOSED'
        elif self.is_connected:
            return 'OPEN'
        else:
            return 'CONNECTING'
    
    # 事件处理器设置方法
    def on_message(self, handler: Callable):
        """设置消息接收处理器"""
        self.on_message_handler = handler
        return handler
    
    def on_error(self, handler: Callable):
        """设置错误处理器"""
        self.on_error_handler = handler
        return handler
    
    def on_connect(self, handler: Callable):
        """设置连接成功处理器"""
        self.on_connect_handler = handler
        return handler
    
    def on_disconnect(self, handler: Callable):
        """设置断开连接处理器"""
        self.on_disconnect_handler = handler
        return handler


class WebSocketManager:
    """
    WebSocket连接管理器
    用于管理多个WebSocket连接
    """
    
    def __init__(self):
        self.clients: Dict[str, WebSocketClient] = {}
        self.logger = logging.getLogger('WebSocketManager')
    
    def create_client(self, name: str, **kwargs) -> WebSocketClient:
        """
        创建新的WebSocket客户端
        
        Args:
            name: 客户端名称
            **kwargs: 传递给WebSocketClient的参数
            
        Returns:
            WebSocketClient: 创建的客户端实例
        """
        client = WebSocketClient(**kwargs)
        self.clients[name] = client
        return client
    
    def get_client(self, name: str) -> Optional[WebSocketClient]:
        """获取指定名称的客户端"""
        return self.clients.get(name)
    
    async def connect_all(self):
        """连接所有客户端"""
        tasks = []
        for name, client in self.clients.items():
            if client._url:  # 只连接已配置URL的客户端
                tasks.append(client.connect(client._url, client._headers, client._ssl_context))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def close_all(self):
        """关闭所有连接"""
        tasks = []
        for client in self.clients.values():
            if client.is_connection_open():
                tasks.append(client.close())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def list_clients(self) -> Dict[str, str]:
        """列出所有客户端及其状态"""
        return {
            name: client.get_connection_state()
            for name, client in self.clients.items()
        }


# 便捷函数
async def create_websocket_client(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> WebSocketClient:
    """
    创建并连接WebSocket客户端的便捷函数
    
    Args:
        url: WebSocket服务器地址
        headers: 自定义请求头
        **kwargs: 其他参数
        
    Returns:
        WebSocketClient: 已连接的客户端实例
    """
    client = WebSocketClient(**kwargs)
    await client.connect(url, headers)
    return client


if __name__ == "__main__":
    # 简单测试
    async def test_websocket():
        """测试WebSocket客户端"""
        client = WebSocketClient()
        
        # 设置事件处理器
        @client.on_message
        async def handle_message(message):
            print(f"📩 收到消息: {message}")
        
        @client.on_error
        async def handle_error(error):
            print(f"❌ 发生错误: {error}")
        
        @client.on_connect
        async def handle_connect():
            print("✅ 连接成功")
        
        @client.on_disconnect
        async def handle_disconnect(reason):
            print(f"🔌 连接断开: {reason}")
        
        # 连接到测试服务器
        headers = {
            'Authorization': 'Bearer test-token',
            'X-Client-Type': 'Python-Test-Client'
        }
        
        success = await client.connect('wss://echo.websocket.org', headers=headers)
        
        if success:
            # 发送测试消息
            await client.send("Hello from Python!")
            await client.send({
                "type": "test",
                "message": "这是JSON消息",
                "timestamp": time.time()
            })
            
            # 等待5秒
            await asyncio.sleep(5)
            
            # 关闭连接
            await client.close()
    
    # 运行测试
    asyncio.run(test_websocket())
