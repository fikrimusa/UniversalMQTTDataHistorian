import sqlite3
import json
from datetime import datetime

def initDatabase():
	conn = sqlite3.connect('mqttData.db')
	cursor = conn.cursor()
	
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS mqttMessages(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			topic TEXT NOT NULL,
			payload TEXT NOT NULL,
			qos INTEGER DEFAULT 0,
			retained INTEGER DEFAULT FALSE
		)
	''')
	
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS sensorData (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			deviceId TEXT,
			sensorType TEXT,
			value REAL,
			unit TEXT,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			rawTopic TEXT
		)
	''')
	
	conn.commit()
	conn.close()
	print("Database initialized.")

def saveMessage(topic, payload, qos=0, retained=False):
	conn = sqlite3.connect('mqttData.db')
	cursor = conn.cursor()
	
	cursor.execute('''
		INSERT INTO mqttMessages (topic, payload, qos, retained)
		VALUES (?, ?, ?, ?)
	''', (topic, payload, qos, int(retained)))
	
	conn.commit()
	conn.close()
	return cursor.lastrowid

def getRecentMessages(limit=10):
	conn = sqlite3.connect('mqttData.db')
	cursor = conn.cursor()
	
	cursor.execute('''
		SELECT id, timestamp, topic, payload
		FROM mqttMessages
		ORDER BY timestamp DESC
		LIMIT ?
	''', (limit,))
	
	messages = cursor.fetchall()
	conn.close()
	
	return [
		{
			"id": msg[0],
			"timestamp": msg[1],
			"topic": msg[2],
			"payload": msg[3]
		} 
		for msg in messages
	]

def getMessageCount():
    conn = sqlite3.connect('mqttData.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM mqttMessages')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def getUniqueTopics():
    conn = sqlite3.connect('mqttData.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT topic FROM mqttMessages')
    topics = [row[0] for row in cursor.fetchall()]
    conn.close()
    return topics