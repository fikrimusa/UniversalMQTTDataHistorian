import json
import re
from datetime import datetime

class MessageParser:
    @staticmethod
    def parseMessage(topic, payload, qos=0, retain=False):
        try:
            try:
                data = json.loads(payload)
                return {
                    "format": "json",
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                    "topicStructure": topic.split('/'),
                    "mqttMetadata": {
                        "qos": qos,
                        "retained": retain,
                        "topic": topic
                    }
                }
            except json.JSONDecodeError:
                return {
                    "format": "text", 
                    "data": payload,
                    "timestamp": datetime.now().isoformat(),
                    "topicStructure": topic.split('/'),
                    "length": len(payload),
                    "mqttMetadata": {
                        "qos": qos,
                        "retained": retain, 
                        "topic": topic
                    }
                }
                
        except Exception as e:
            return {
                "format": "error",
                "error": str(e),
                "rawPayload": payload,
                "timestamp": datetime.now().isoformat(),
                "mqttMetadata": {
                    "qos": qos,
                    "retained": retain,
                    "topic": topic
                }
            }
    
    @staticmethod
    def extractSensorData(topic, payload, qos=0, retain=False):
        parsed = MessageParser.parseMessage(topic, payload, qos, retain)
        
        sensorTypes = ['temperature', 'humidity', 'pressure', 'voltage', 'status', 'sensor', 'data']
        detectedSensors = []
        
        for segment in parsed['topicStructure']:
            for sensorType in sensorTypes:
                if sensorType in segment.lower():
                    detectedSensors.append(segment)
                    break
        
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", str(payload))
        
        parsed['sensorInfo'] = {
            'detectedSensors': detectedSensors,
            'numericValues': [float(num) for num in numbers] if numbers else [],
            'isSensorData': len(detectedSensors) > 0 or len(numbers) > 0
        }
        
        return parsed

    @staticmethod
    def analyzeTopicPattern(topic):
        segments = topic.split('/')
        
        patterns = {
            'hasDeviceId': len(segments) >= 2 and (segments[1].isdigit() or any(char.isdigit() for char in segments[1])),
            'hasSensorType': any(sensor in topic.lower() for sensor in ['temperature', 'humidity', 'pressure', 'sensor']),
            'isControlTopic': any(keyword in topic.lower() for keyword in ['cmd', 'control', 'set', 'command']),
            'isStatusTopic': any(keyword in topic.lower() for keyword in ['status', 'state', 'online', 'offline']),
            'depth': len(segments),
            'segments': segments
        }
        
        return patterns

    @staticmethod
    def parseAndSave(messageId, topic, payload, qos=0, retain=False):
        parsedData = MessageParser.extractSensorData(topic, payload, qos, retain)
        parsedData['messageId'] = messageId
        return parsedData