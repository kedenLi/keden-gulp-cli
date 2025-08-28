# Node.js WebSocket 客户端

这是一个功能完整的Node.js WebSocket客户端，支持自定义请求头、自动重连、心跳检测等功能。

## 功能特性

- ✅ 支持自定义请求头
- ✅ 自动重连机制
- ✅ 心跳检测（Ping/Pong）
- ✅ JSON消息支持
- ✅ 错误处理和状态管理
- ✅ 优雅关闭连接
- ✅ TypeScript友好的API设计

## 安装依赖

```bash
npm install
```

## 快速开始

### 1. 基本使用

```javascript
const WebSocketClient = require('./websocket-client');

const client = new WebSocketClient();

// 配置请求头
const options = {
    headers: {
        'Authorization': 'Bearer your-token',
        'X-API-Key': 'your-api-key',
        'Origin': 'https://your-domain.com'
    }
};

// 连接到WebSocket服务器
client.connect('wss://your-websocket-server.com', options)
    .then(() => {
        console.log('连接成功！');
        client.send('Hello, Server!');
    })
    .catch(error => {
        console.error('连接失败:', error);
    });
```

### 2. 运行示例

```bash
# 运行完整示例
npm start

# 运行简单测试
npm test
```

## API 文档

### WebSocketClient 类

#### 构造函数

```javascript
const client = new WebSocketClient();
```

#### 主要方法

##### connect(url, options)

连接到WebSocket服务器。

**参数:**
- `url` (string): WebSocket服务器地址
- `options` (Object): 连接选项
  - `headers` (Object): 自定义请求头
  - `protocols` (Array): WebSocket协议列表
  - `timeout` (number): 连接超时时间（毫秒）

**返回:** Promise

##### send(message)

发送消息到服务器。

**参数:**
- `message` (string|Object): 要发送的消息

**返回:** boolean - 发送是否成功

##### close(code, reason)

关闭WebSocket连接。

**参数:**
- `code` (number): 关闭代码（可选，默认1000）
- `reason` (string): 关闭原因（可选）

##### ping(data)

发送心跳检测消息。

**参数:**
- `data` (string): Ping数据（可选）

#### 事件处理方法（可重写）

##### onMessage(message)

处理接收到的消息。

```javascript
client.onMessage = function(message) {
    console.log('收到消息:', message);
};
```

##### onError(error)

处理WebSocket错误。

```javascript
client.onError = function(error) {
    console.error('发生错误:', error);
};
```

#### 状态查询方法

##### isConnectionOpen()

检查连接是否打开。

**返回:** boolean

##### getConnectionState()

获取当前连接状态。

**返回:** string - 'CONNECTING' | 'OPEN' | 'CLOSING' | 'CLOSED' | 'DISCONNECTED'

## 请求头配置示例

```javascript
const headers = {
    // 认证相关
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...',
    'X-API-Key': 'your-api-key-here',
    
    // 客户端信息
    'User-Agent': 'MyApp/1.0.0 (Node.js WebSocket Client)',
    'X-Client-Version': '1.0.0',
    'X-Client-Platform': 'Node.js',
    
    // 会话相关
    'X-Session-ID': 'session-12345',
    'X-Request-ID': 'req-' + Date.now(),
    
    // 其他自定义头
    'Origin': 'https://myapp.com',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Custom-Header': 'custom-value'
};
```

## 高级用法

### 继承扩展

```javascript
class CustomWebSocketClient extends WebSocketClient {
    constructor() {
        super();
        this.messageHistory = [];
    }

    onMessage(message) {
        // 保存消息历史
        this.messageHistory.push({
            message,
            timestamp: new Date()
        });
        
        // 调用父类方法
        super.onMessage(message);
    }

    getMessageHistory() {
        return this.messageHistory;
    }
}
```

### 错误处理和重连

客户端内置了自动重连机制：
- 最大重连次数：5次
- 重连间隔：3秒
- 只在非正常关闭时触发重连

## 注意事项

1. 确保Node.js版本 >= 14.0.0
2. 网络环境要支持WebSocket协议
3. 服务器需要支持您配置的请求头
4. 生产环境建议添加更完善的错误处理

## 许可证

MIT License
