// src/services/websocket.js

class WebSocketService {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000;
        this.listeners = {};
    }

    connect(url) {
        try {
            this.socket = new WebSocket(url);

            this.socket.onopen = (event) => {
                console.log('WebSocket连接已建立');
                this.reconnectAttempts = 0;
                this.emit('open', event);
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('收到消息:', data);
                    this.emit('message', data);
                } catch (error) {
                    console.error('解析消息失败:', error);
                }
            };

            this.socket.onclose = (event) => {
                console.log('WebSocket连接已关闭');
                this.emit('close', event);
                this.handleReconnect();
            };

            this.socket.onerror = (error) => {
                console.error('WebSocket错误:', error);
                this.emit('error', error);
            };

        } catch (error) {
            console.error('WebSocket连接失败:', error);
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        } else {
            console.error('WebSocket未连接');
        }
    }

    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`尝试重连... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.connect(this.lastUrl);
            }, this.reconnectInterval);
        }
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }
}

export default new WebSocketService();
