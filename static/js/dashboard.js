class Dashboard {
    constructor() {
        this.baseUrl = window.location.origin;
        this.ws = null;
        this.messageCount = 0;
        this.init();
    }

    init() {
        this.loadStats();
        this.loadMessages();
        this.loadSensors();
        this.initWebSocket();

        // Poll for queued messages every second
        setInterval(() => {
            this.pollForNewMessages();
        }, 1000);

        // Refresh stats every 5 seconds
        setInterval(() => {
            this.loadStats();
        }, 5000);
    }

    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleRealTimeUpdate(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus(true);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus(false);
            // Try to reconnect after 3 seconds
            setTimeout(() => this.initWebSocket(), 3000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus(false);
        };
    }

    // ADD THIS NEW METHOD
    async pollForNewMessages() {
        try {
            const response = await fetch(`${this.baseUrl}/api/queued-messages`);
            const data = await response.json();

            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    this.handleRealTimeUpdate(message);
                });
            }
        } catch (error) {
            console.error('Error polling for messages:', error);
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('websocketStatus');
        if (statusElement) {
            statusElement.textContent = connected ? 'Connected' : 'Disconnected';
            statusElement.className = connected ? 'status-connected' : 'status-disconnected';
        }
    }

    handleRealTimeUpdate(data) {
        if (data.type === 'new_message') {
            this.addNewMessage(data);
            this.updateStats();
            this.checkForSensorData(data);
        }
    }

    addNewMessage(messageData) {
        const messagesContainer = document.getElementById('messageList');
        if (!messagesContainer) return;

        const messageElement = document.createElement('div');
        messageElement.className = 'message-item new-message';
        messageElement.innerHTML = `
            <div class="topic">${this.escapeHtml(messageData.topic)}</div>
            <div class="payload">${this.escapeHtml(messageData.payload)}</div>
            <div class="timestamp">${new Date(messageData.timestamp).toLocaleString()}</div>
        `;

        // Add to top
        messagesContainer.insertBefore(messageElement, messagesContainer.firstChild);

        // Limit to 20 messages
        while (messagesContainer.children.length > 20) {
            messagesContainer.removeChild(messagesContainer.lastChild);
        }

        // Remove highlight after 2 seconds
        setTimeout(() => {
            messageElement.classList.remove('new-message');
        }, 2000);
    }

    updateStats() {
        this.messageCount++;
        const totalEl = document.getElementById('totalMessages');
        if (totalEl) {
            totalEl.textContent = this.messageCount.toLocaleString();
        }
    }

    checkForSensorData(messageData) {
        // Check if this message contains sensor data and update sensor cards
        if (messageData.parsedData && messageData.parsedData.sensorInfo && messageData.parsedData.sensorInfo.isSensorData) {
            this.loadSensors(); // Reload sensors when new sensor data arrives
        }
    }

    async loadStats() {
        try {
            const response = await fetch(`${this.baseUrl}/api/stats`);
            const data = await response.json();

            document.getElementById('totalMessages').textContent = data.totalMessages.toLocaleString();
            document.getElementById('uniqueTopics').textContent = data.uniqueTopics;

            const mqttStatus = document.getElementById('mqttStatus');
            if (mqttStatus) {
                mqttStatus.textContent = data.mqttConnected ? 'Connected' : 'Disconnected';
                mqttStatus.className = data.mqttConnected ? 'status-connected' : 'status-disconnected';
            }

        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async loadMessages() {
        try {
            const response = await fetch(`${this.baseUrl}/api/messages?limit=10`);
            const data = await response.json();

            const messagesContainer = document.getElementById('messageList');
            if (!messagesContainer) return;

            messagesContainer.innerHTML = '';

            data.messages.forEach(msg => {
                const messageElement = document.createElement('div');
                messageElement.className = 'message-item';
                messageElement.innerHTML = `
                    <div class="topic">${this.escapeHtml(msg.topic)}</div>
                    <div class="payload">${this.escapeHtml(msg.payload)}</div>
                    <div class="timestamp">${new Date(msg.timestamp).toLocaleString()}</div>
                `;
                messagesContainer.appendChild(messageElement);
            });

        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }

    async loadSensors() {
        try {
            const response = await fetch(`${this.baseUrl}/api/sensors/latest`);
            const data = await response.json();

            const sensorsContainer = document.getElementById('sensorsGrid');
            if (!sensorsContainer) return;

            sensorsContainer.innerHTML = '';

            data.sensors.forEach(sensor => {
                const sensorElement = document.createElement('div');
                sensorElement.className = 'sensor-card';
                sensorElement.innerHTML = `
                    <h3>${this.escapeHtml(sensor.sensorType)}</h3>
                    <div class="sensor-value">${sensor.value}</div>
                    <div class="sensor-unit">${sensor.unit || ''}</div>
                    <div class="sensor-location">Location: ${sensor.location || 'Unknown'}</div>
                    <div class="timestamp">${new Date(sensor.timestamp).toLocaleString()}</div>
                `;
                sensorsContainer.appendChild(sensorElement);
            });

        } catch (error) {
            console.error('Error loading sensors:', error);
        }
    }

    escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return unsafe;
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});