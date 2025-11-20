from fastapi import FastAPI
import uvicorn
import threading
import time
from database import initDatabase, getRecentMessages
from mqttClient import startMqttClient, mqttClient

app = FastAPI(
    title="Universal MQTT Data Historian",
    description="Real-time MQTT data storage and API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Universal MQTT Data Historian API",
        "docs": "Visit /docs for API documentation",
        "endpoints": [
            "/docs - Interactive API docs",
            "/messages - Get stored messages", 
            "/status - System status",
            "/topics - Discovered topics"
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
    
    print("Starting FastAPI server on http://0.0.0.0:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Dashboard: http://localhost:8000/")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")