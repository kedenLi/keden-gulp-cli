# Python WebSocket 客户端

这是一个功能完整的Python WebSocket客户端，基于`websockets`库开发，支持自定义请求头、自动重连、心跳检测等高级功能。

## 🚀 功能特性

- ✅ **自定义请求头支持** - 在握手阶段发送认证信息
- ✅ **异步事件驱动** - 基于asyncio的高性能异步处理
- ✅ **自动重连机制** - 连接断开时自动尝试重连
- ✅ **心跳检测** - 内置Ping/Pong机制保持连接活跃
- ✅ **JSON消息支持** - 自动处理JSON格式消息
- ✅ **多客户端管理** - WebSocketManager支持管理多个连接
- ✅ **SSL/TLS支持** - 支持安全的WSS连接
- ✅ **完善的日志系统** - 详细的连接和错误日志
- ✅ **事件处理器** - 灵活的事件回调机制
- ✅ **类型提示** - 完整的类型注解支持

## 📦 安装依赖

```bash
# 安装基础依赖
pip install websockets

# 或安装完整依赖（包括开发工具）
pip install -r requirements.txt
```

## 🔧 快速开始

### 基本使用

```python
import asyncio
from websocket_client import WebSocketClient

async def main():
    client = WebSocketClient()
    
    # 配置请求头（仅在握手阶段有效）
    headers = {
        'Authorization': 'Bearer your-token',
        'X-API-Key': 'your-api-key'
    }
    
    # 设置消息处理器
    @client.on_message
    async def handle_message(message):
        print(f"收到消息: {message}")
    
    # 连接到WebSocket服务器
    await client.connect('wss://your-server.com', headers=headers)
    
    # 发送消息
    await client.send("Hello, Server!")
    await client.send({"type": "greeting", "data": "JSON消息"})
    
    # 等待一段时间
    await asyncio.sleep(5)
    
    # 关闭连接
    await client.close()

# 运行
asyncio.run(main())
```

### 便捷函数

```python
from websocket_client import create_websocket_client

async def quick_example():
    # 快速创建并连接
    client = await create_websocket_client(
        'wss://echo.websocket.org',
        headers={'Authorization': 'Bearer token'}
    )
    
    await client.send("Hello!")
    await asyncio.sleep(2)
    await client.close()
```

## 📚 API 文档

### WebSocketClient 类

#### 主要方法

##### `connect(url, headers=None, ssl_context=None, **kwargs)`

连接到WebSocket服务器。

**参数:**
- `url` (str): WebSocket服务器地址
- `headers` (dict, 可选): 自定义请求头（仅握手阶段有效）
- `ssl_context` (ssl.SSLContext, 可选): SSL上下文
- `**kwargs`: 其他连接参数

**返回:** `bool` - 连接是否成功

```python
headers = {
    'Authorization': 'Bearer token123',
    'X-Client-Version': '1.0.0',
    'User-Agent': 'MyApp/1.0'
}

success = await client.connect('wss://api.example.com', headers=headers)
```

##### `send(message)`

发送消息到服务器。

**参数:**
- `message` (str | dict): 要发送的消息

**返回:** `bool` - 发送是否成功

```python
# 发送文本消息
await client.send("Hello, Server!")

# 发送JSON消息
await client.send({
    "type": "user_message",
    "content": "Hello from Python!",
    "timestamp": time.time()
})
```

##### `ping(data=b'ping')`

发送心跳检测消息。

**参数:**
- `data` (bytes, 可选): Ping数据

**返回:** `bool` - 心跳是否成功

##### `close(code=1000, reason="正常关闭")`

关闭WebSocket连接。

#### 事件处理器

##### `@client.on_message`

处理接收到的消息。

```python
@client.on_message
async def handle_message(message):
    if isinstance(message, dict):
        print(f"JSON消息: {message}")
    else:
        print(f"文本消息: {message}")
```

##### `@client.on_connect`

连接成功时触发。

```python
@client.on_connect
async def handle_connect():
    print("连接成功!")
    await client.send("连接成功消息")
```

##### `@client.on_error`

发生错误时触发。

```python
@client.on_error
async def handle_error(error):
    print(f"发生错误: {error}")
```

##### `@client.on_disconnect`

连接断开时触发。

```python
@client.on_disconnect
async def handle_disconnect(reason):
    print(f"连接断开: {reason}")
```

#### 状态查询方法

##### `is_connection_open()`

检查连接是否打开。

**返回:** `bool`

##### `get_connection_state()`

获取连接状态。

**返回:** `str` - 'CONNECTING' | 'OPEN' | 'CLOSING' | 'CLOSED' | 'DISCONNECTED'

### WebSocketManager 类

用于管理多个WebSocket连接。

```python
from websocket_client import WebSocketManager

manager = WebSocketManager()

# 创建多个客户端
client1 = manager.create_client("api_client")
client2 = manager.create_client("notification_client")

# 连接所有客户端
await manager.connect_all()

# 查看所有客户端状态
states = manager.list_clients()
print(states)  # {'api_client': 'OPEN', 'notification_client': 'OPEN'}

# 关闭所有连接
await manager.close_all()
```

## 🎯 高级用法

### 自定义客户端类

```python
class MyCustomClient(WebSocketClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_count = 0
        self.user_id = None
    
    async def authenticate(self, user_id, token):
        """自定义认证方法"""
        self.user_id = user_id
        auth_msg = {
            "type": "auth",
            "user_id": user_id,
            "token": token
        }
        await self.send(auth_msg)
    
    async def _handle_message(self, message):
        """重写消息处理"""
        self.message_count += 1
        
        if isinstance(message, dict):
            if message.get('type') == 'auth_response':
                if message.get('success'):
                    self.logger.info("认证成功")
                else:
                    self.logger.error("认证失败")
        
        await super()._handle_message(message)
    
    def get_stats(self):
        """获取统计信息"""
        return {
            "message_count": self.message_count,
            "user_id": self.user_id,
            "connected": self.is_connection_open()
        }

# 使用自定义客户端
client = MyCustomClient()
await client.connect('wss://api.example.com')
await client.authenticate('user123', 'token456')
```

### SSL/TLS配置

```python
import ssl

# 创建SSL上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 或者加载自定义证书
# ssl_context.load_cert_chain('client.crt', 'client.key')
# ssl_context.load_verify_locations('ca.crt')

await client.connect('wss://secure-api.com', ssl_context=ssl_context)
```

## 🔑 请求头配置示例

```python
# 认证相关
headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...',
    'X-API-Key': 'your-api-key-here',
    'X-Auth-Token': 'additional-auth-token',
}

# 客户端信息
headers = {
    'User-Agent': 'MyApp/1.0.0 (Python WebSocket Client)',
    'X-Client-Version': '1.0.0',
    'X-Client-Platform': 'Python',
    'X-Client-OS': 'Linux',
}

# 会话相关
headers = {
    'X-Session-ID': 'session-12345',
    'X-Request-ID': f'req-{int(time.time())}',
    'X-Correlation-ID': 'corr-67890',
}

# 业务相关
headers = {
    'X-User-ID': 'user123',
    'X-Tenant-ID': 'tenant456',
    'X-Device-ID': 'device789',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}
```

## 🧪 运行示例

```bash
# 运行完整示例
python example.py

# 运行简单测试
python test_websocket.py

# 运行特定示例
python -c "import asyncio; from example import basic_example; asyncio.run(basic_example())"
```

## 📝 注意事项

### 请求头限制

1. **请求头仅在握手阶段有效** - 连接建立后无法再发送HTTP请求头
2. **认证建议** - 在连接建立后通过消息进行认证：

```python
# 握手阶段认证（推荐用于初始验证）
headers = {'Authorization': 'Bearer initial-token'}
await client.connect(url, headers=headers)

# 连接后认证（推荐用于业务认证）
await client.send({
    "type": "authenticate",
    "token": "business-token",
    "user_id": "user123"
})
```

### 性能优化

1. **复用连接** - 避免频繁创建和销毁连接
2. **批量发送** - 合并多个小消息
3. **异步处理** - 使用异步事件处理器

### 错误处理

```python
try:
    await client.connect(url, headers=headers)
    await client.send(message)
except ConnectionRefused:
    print("服务器拒绝连接")
except ConnectionClosed:
    print("连接意外关闭")
except Exception as e:
    print(f"其他错误: {e}")
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！
