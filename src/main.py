from fastapi import FastAPI
import uvicorn
import threading
import time
import asyncio
from database import initDatabase, getRecentMessages
from mqttClient import startMqttClient, mqttClient
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from websocketManager import manager, getQueuedMessages, processQueuedMessages

app = FastAPI(
    title="Universal MQTT Data Historian",
    description="Real-time MQTT data storage and API",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {
        "message": "Welcome to the Universal MQTT Data Historian API",
        "docs": "Visit /docs for API documentation",
        "endpoints": [
            "/docs - Interactive API docs",
            "/messages - Get stored messages", 
            "/status - System status",
            "/topics - Discovered topics",
            "/dashboard - Web Dashboard",
            "/api/stats - System statistics",
            "/api/queued-messages - Get queued messages"
        ]
    }

@app.get("/status")
def status():
    return {
        "status": "healthy",
        "service": "MQTT Data Historian",
        "mqttConnected": mqttClient.connected,
        "timestamp": time.time()
    }

@app.get("/messages")
def getMessages(limit: int = 10):
    messages = getRecentMessages(limit)
    return {
        "count": len(messages),
        "limit": limit,
        "messages": messages
    }

@app.get("/topics")
def getTopics(limit: int = 20):
    messages = getRecentMessages(limit)
    topics = {}
    
    for msg in messages:
        topic = msg['topic']
        if topic in topics:
            topics[topic] += 1
        else:
            topics[topic] = 1
    
    return {
        "uniqueTopicsCount": len(topics),
        "topics": topics
    }

@app.post("/publish/{topic}")
def publishMessage(topic: str, message: str):
    print(f"PUBLISH ENDPOINT CALLED: topic={topic}, message={message}")
    if mqttClient.connected:
        mqttClient.publishMessage(topic, message)
        return {
            "status": "published",
            "topic": topic, 
            "message": message
        }
    else:
        return {
            "status": "error",
            "message": "MQTT client not connected"
        }

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/stats")
async def get_stats():
    from database import getMessageCount, getUniqueTopics
    return {
        "totalMessages": getMessageCount(),
        "uniqueTopics": len(getUniqueTopics()),
        "mqttConnected": mqttClient.connected
    }

@app.get("/api/queued-messages")
async def get_queued_messages():
    """Get queued messages for polling"""
    messages = getQueuedMessages()
    return {"messages": messages}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Process queued messages and keep connection alive
            await processQueuedMessages()
            await websocket.receive_text()  # Keep this for connection keep-alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ADD THIS BACKGROUND TASK FUNCTION
async def process_queued_messages_background():
    """Background task to process queued messages"""
    while True:
        await processQueuedMessages()
        await asyncio.sleep(0.5)  # Process every 500ms

def startBackgroundServices():
    print("Starting background services")
    if startMqttClient():
        print("MQTT client started - capturing real IoT data")
    else:
        print("Failed to start MQTT client")

if __name__ == "__main__":
    initDatabase()
    print("Database initialized")

    mqttThread = threading.Thread(target=startBackgroundServices, daemon=True)
    mqttThread.start()
    
    # Start background task for processing queued messages
    import asyncio
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(process_queued_messages_background())
    
    print("Starting FastAPI server on http://0.0.0.0:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Dashboard: http://localhost:8000/dashboard")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")