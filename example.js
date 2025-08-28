const WebSocketClient = require('./websocket-client');

/**
 * WebSocket客户端使用示例
 * 演示如何连接到WebSocket服务器并发送/接收消息
 */
async function main() {
    // 创建WebSocket客户端实例
    const client = new WebSocketClient();

    // 配置连接选项，包括自定义请求头
    const options = {
        headers: {
            'Authorization': 'Bearer your-token-here',
            'X-Client-Version': '1.0.0',
            'X-User-Agent': 'Custom-WebSocket-Client',
            'X-API-Key': 'your-api-key-here',
            'Origin': 'https://your-domain.com',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Custom-Header': 'custom-value'
        },
        protocols: ['websocket'], // 可选：指定协议
        timeout: 10000 // 连接超时时间（毫秒）
    };

    try {
        // 连接到WebSocket服务器
        // 注意：这里使用的是测试服务器，您需要替换为实际的WebSocket服务器地址
        const wsUrl = 'wss://echo.websocket.org'; // 示例WebSocket回声服务器
        
        console.log('开始连接WebSocket服务器...');
        await client.connect(wsUrl, options);

        // 重写消息处理函数
        client.onMessage = function(message) {
            console.log('📩 收到服务器消息:', message);
            
            // 如果是JSON消息，可以进行特殊处理
            if (typeof message === 'object') {
                console.log('这是一个JSON消息:', JSON.stringify(message, null, 2));
            }
        };

        // 重写错误处理函数
        client.onError = function(error) {
            console.error('❌ WebSocket发生错误:', error.message);
        };

        // 发送测试消息
        console.log('发送测试消息...');
        
        // 发送简单文本消息
        client.send('Hello, WebSocket Server!');
        
        // 等待一秒后发送JSON消息
        setTimeout(() => {
            const jsonMessage = {
                type: 'greeting',
                data: {
                    message: '你好，这是一个JSON消息',
                    timestamp: new Date().toISOString(),
                    userId: 'user123'
                }
            };
            client.send(jsonMessage);
        }, 1000);

        // 等待两秒后发送ping消息
        setTimeout(() => {
            client.ping('心跳检测');
        }, 2000);

        // 定期发送消息（每5秒）
        const messageInterval = setInterval(() => {
            if (client.isConnectionOpen()) {
                const periodicMessage = {
                    type: 'periodic',
                    message: '定期消息',
                    timestamp: new Date().toISOString()
                };
                client.send(periodicMessage);
            } else {
                console.log('连接已断开，停止发送定期消息');
                clearInterval(messageInterval);
            }
        }, 5000);

        // 监听进程退出信号，优雅关闭连接
        process.on('SIGINT', () => {
            console.log('\n收到退出信号，正在关闭WebSocket连接...');
            clearInterval(messageInterval);
            client.close(1000, '客户端主动关闭');
            process.exit(0);
        });

        // 10秒后自动关闭连接（用于演示）
        setTimeout(() => {
            console.log('演示结束，关闭连接...');
            clearInterval(messageInterval);
            client.close(1000, '演示完成');
        }, 10000);

    } catch (error) {
        console.error('连接WebSocket服务器失败:', error.message);
        process.exit(1);
    }
}

/**
 * 扩展示例：自定义WebSocket客户端类
 */
class CustomWebSocketClient extends WebSocketClient {
    constructor() {
        super();
        this.messageQueue = []; // 消息队列
        this.isAuthenticated = false;
    }

    /**
     * 重写消息处理函数
     */
    onMessage(message) {
        console.log('🔔 自定义客户端收到消息:', message);
        
        // 处理认证响应
        if (typeof message === 'object' && message.type === 'auth_response') {
            if (message.success) {
                this.isAuthenticated = true;
                console.log('✅ 认证成功');
                // 发送队列中的消息
                this.flushMessageQueue();
            } else {
                console.log('❌ 认证失败:', message.error);
            }
        }
        
        // 存储消息到队列
        this.messageQueue.push({
            message: message,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * 发送认证消息
     */
    authenticate(token) {
        const authMessage = {
            type: 'authenticate',
            token: token
        };
        this.send(authMessage);
    }

    /**
     * 发送队列中的消息
     */
    flushMessageQueue() {
        console.log(`发送队列中的 ${this.messageQueue.length} 条消息`);
        // 这里可以实现实际的消息发送逻辑
    }

    /**
     * 获取消息历史
     */
    getMessageHistory() {
        return this.messageQueue;
    }
}

// 运行示例
if (require.main === module) {
    main().catch(error => {
        console.error('程序执行失败:', error);
        process.exit(1);
    });
}

module.exports = { CustomWebSocketClient };
