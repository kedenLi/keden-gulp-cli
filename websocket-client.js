const WebSocket = require('ws');

/**
 * WebSocket客户端类
 * 支持自定义请求头和连接配置
 */
class WebSocketClient {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000; // 重连间隔3秒
    }

    /**
     * 连接到WebSocket服务器
     * @param {string} url - WebSocket服务器地址
     * @param {Object} options - 连接选项
     * @param {Object} options.headers - 自定义请求头
     * @param {Object} options.protocols - 协议列表
     * @param {number} options.timeout - 连接超时时间
     */
    connect(url, options = {}) {
        try {
            // 默认请求头配置
            const defaultHeaders = {
                'User-Agent': 'Node.js WebSocket Client',
                'Accept': '*/*',
                'Cache-Control': 'no-cache'
            };

            // 合并自定义请求头
            const headers = { ...defaultHeaders, ...options.headers };

            // WebSocket连接配置
            const wsOptions = {
                headers: headers,
                handshakeTimeout: options.timeout || 10000,
                perMessageDeflate: false
            };

            // 如果有协议，添加到配置中
            if (options.protocols) {
                wsOptions.protocols = options.protocols;
            }

            console.log('正在连接到WebSocket服务器:', url);
            console.log('请求头信息:', headers);

            // 创建WebSocket连接
            this.ws = new WebSocket(url, wsOptions);

            // 设置事件监听器
            this.setupEventListeners();

            return new Promise((resolve, reject) => {
                this.ws.once('open', () => {
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    console.log('WebSocket连接成功建立');
                    resolve(this);
                });

                this.ws.once('error', (error) => {
                    console.error('WebSocket连接错误:', error.message);
                    reject(error);
                });
            });

        } catch (error) {
            console.error('创建WebSocket连接时发生错误:', error.message);
            throw error;
        }
    }

    /**
     * 设置WebSocket事件监听器
     */
    setupEventListeners() {
        // 连接打开事件
        this.ws.on('open', () => {
            console.log('WebSocket连接已打开');
        });

        // 接收消息事件
        this.ws.on('message', (data) => {
            try {
                const message = data.toString();
                console.log('收到消息:', message);
                
                // 尝试解析JSON消息
                try {
                    const jsonMessage = JSON.parse(message);
                    this.onMessage(jsonMessage);
                } catch (e) {
                    // 如果不是JSON格式，直接处理原始消息
                    this.onMessage(message);
                }
            } catch (error) {
                console.error('处理接收消息时发生错误:', error.message);
            }
        });

        // 连接关闭事件
        this.ws.on('close', (code, reason) => {
            this.isConnected = false;
            console.log(`WebSocket连接已关闭 - 代码: ${code}, 原因: ${reason || '无'}`);
            
            // 如果不是正常关闭，尝试重连
            if (code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.attemptReconnect();
            }
        });

        // 错误事件
        this.ws.on('error', (error) => {
            console.error('WebSocket发生错误:', error.message);
            this.onError(error);
        });

        // Ping/Pong心跳检测
        this.ws.on('ping', (data) => {
            console.log('收到ping:', data.toString());
            this.ws.pong(data);
        });

        this.ws.on('pong', (data) => {
            console.log('收到pong:', data.toString());
        });
    }

    /**
     * 尝试重连
     */
    attemptReconnect() {
        this.reconnectAttempts++;
        console.log(`尝试重连... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            if (this.lastUrl && this.lastOptions) {
                this.connect(this.lastUrl, this.lastOptions)
                    .catch(error => {
                        console.error('重连失败:', error.message);
                    });
            }
        }, this.reconnectInterval);
    }

    /**
     * 发送消息
     * @param {string|Object} message - 要发送的消息
     */
    send(message) {
        if (!this.isConnected || this.ws.readyState !== WebSocket.OPEN) {
            console.error('WebSocket未连接，无法发送消息');
            return false;
        }

        try {
            let data;
            if (typeof message === 'object') {
                data = JSON.stringify(message);
            } else {
                data = message.toString();
            }

            this.ws.send(data);
            console.log('消息已发送:', data);
            return true;
        } catch (error) {
            console.error('发送消息时发生错误:', error.message);
            return false;
        }
    }

    /**
     * 发送Ping消息进行心跳检测
     * @param {string} data - Ping数据
     */
    ping(data = 'ping') {
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.ping(data);
            console.log('发送ping:', data);
        }
    }

    /**
     * 关闭WebSocket连接
     * @param {number} code - 关闭代码
     * @param {string} reason - 关闭原因
     */
    close(code = 1000, reason = '正常关闭') {
        if (this.ws) {
            this.isConnected = false;
            this.ws.close(code, reason);
            console.log('WebSocket连接已主动关闭');
        }
    }

    /**
     * 检查连接状态
     * @returns {boolean} 是否已连接
     */
    isConnectionOpen() {
        return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN;
    }

    /**
     * 获取WebSocket状态
     * @returns {string} 连接状态描述
     */
    getConnectionState() {
        if (!this.ws) return 'DISCONNECTED';
        
        switch (this.ws.readyState) {
            case WebSocket.CONNECTING:
                return 'CONNECTING';
            case WebSocket.OPEN:
                return 'OPEN';
            case WebSocket.CLOSING:
                return 'CLOSING';
            case WebSocket.CLOSED:
                return 'CLOSED';
            default:
                return 'UNKNOWN';
        }
    }

    /**
     * 消息接收处理函数（可重写）
     * @param {string|Object} message - 接收到的消息
     */
    onMessage(message) {
        // 子类可以重写此方法来处理接收到的消息
        console.log('处理接收到的消息:', message);
    }

    /**
     * 错误处理函数（可重写）
     * @param {Error} error - 错误对象
     */
    onError(error) {
        // 子类可以重写此方法来处理错误
        console.error('WebSocket错误处理:', error.message);
    }
}

module.exports = WebSocketClient;
