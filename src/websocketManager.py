from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_message(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

# Global instance
manager = ConnectionManager()

# Message queue for MQTT messages
messageQueue = []

def addMessageToQueue(message: dict):
    """Add message to queue from MQTT thread"""
    messageQueue.append(message)

def getQueuedMessages():
    """Get all queued messages and clear the queue"""
    messages = messageQueue.copy()
    messageQueue.clear()
    return messages

async def processQueuedMessages():
    """Process queued messages and broadcast via WebSocket"""
    messages = getQueuedMessages()
    for message in messages:
        await manager.broadcast_message(message)