const WebSocketClient = require('./websocket-client');

/**
 * 简单的WebSocket测试脚本
 * 用于快速测试WebSocket连接和消息发送
 */
async function testWebSocket() {
    console.log('🚀 开始WebSocket连接测试...\n');

    const client = new WebSocketClient();

    // 配置请求头
    const headers = {
        'Authorization': 'Bearer test-token-123',
        'X-Client-Type': 'Test-Client',
        'X-Session-ID': 'session-' + Date.now(),
        'User-Agent': 'Node.js WebSocket Test Client'
    };

    try {
        // 连接到测试服务器
        console.log('📡 正在连接到WebSocket测试服务器...');
        await client.connect('wss://echo.websocket.org', { headers });

        // 简单的消息处理
        client.onMessage = (message) => {
            console.log('📨 服务器回应:', message);
        };

        // 发送测试消息
        console.log('📤 发送测试消息...');
        client.send('这是一个测试消息：' + new Date().toLocaleString('zh-CN'));

        // 发送JSON消息
        setTimeout(() => {
            const jsonMsg = {
                type: 'test',
                content: '这是JSON格式的测试消息',
                timestamp: Date.now()
            };
            client.send(jsonMsg);
        }, 1000);

        // 3秒后关闭连接
        setTimeout(() => {
            console.log('✅ 测试完成，关闭连接');
            client.close();
            process.exit(0);
        }, 3000);

    } catch (error) {
        console.error('❌ 测试失败:', error.message);
        process.exit(1);
    }
}

// 运行测试
testWebSocket();
