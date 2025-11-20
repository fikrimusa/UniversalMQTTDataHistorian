import paho.mqtt.client as mqtt
import time
from database import saveMessage
from messageParser import MessageParser

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.connected = False
        self.messageCount = 0

    def onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("Connected to MQTT Broker")
            topics = [
                "codePower/#",
                "codePower/sensors/#",
                "codePower/test/#",
                "codePower/iot/#"
            ]
            for topic in topics:
                client.subscribe(topic)
                print(f"Subscribed to: {topic}")
        else:
            print(f"Failed to connect, return code {rc}")

    def onMessage(self, client, userdata, msg):
        try:
            self.messageCount += 1
            payload = msg.payload.decode('utf-8')
            
            parsedData = MessageParser.extractSensorData(
                topic=msg.topic,
                payload=payload,
                qos=msg.qos,
                retain=msg.retain
            )
            
            messageId = saveMessage(
                topic=msg.topic, 
                payload=payload,
                qos=msg.qos,
                retained=msg.retain
            )
            
            sensorInfo = parsedData['sensorInfo']
            if sensorInfo['isSensorData'] and sensorInfo['numericValues']:
                values = sensorInfo['numericValues']
                print(f"Message [{messageId}] {msg.topic} -> {values}")
            elif parsedData['format'] == 'json':
                print(f"Message [{messageId}] {msg.topic} -> JSON data")
            else:
                preview = payload[:40] + "..." if len(payload) > 40 else payload
                print(f"Message [{messageId}] {msg.topic} -> {preview}")
                
        except Exception as e:
            print(f"Error processing message: {e}")

    def connect(self):
        try:
            print("Connecting to MQTT broker")
            self.client.connect("test.mosquitto.org", 1883, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
            
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT client disconnected")

    def publishMessage(self, topic, message):
        if self.connected:
            result = self.client.publish(topic, message)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published to {topic}: {message}")
                return True
            else:
                print(f"Failed to publish to {topic}")
                return False
        else:
            print("Not connected to MQTT broker")
            return False

mqttClient = MQTTClient()

def startMqttClient():
    return mqttClient.connect()

def stopMqttClient():
    mqttClient.disconnect()

def publishMessage(topic, message):
    mqttClient.publishMessage(topic, message)