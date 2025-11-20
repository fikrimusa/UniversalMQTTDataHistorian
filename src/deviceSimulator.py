import time
import random
import json
from mqttClient import startMqttClient, publishMessage, stopMqttClient

class DeviceSimulator:
    def __init__(self):
        self.devices = {
            "sensor01": {"type": "temperature", "location": "room1", "min": 20, "max": 30},
            "sensor02": {"type": "humidity", "location": "room1", "min": 40, "max": 80},
            "sensor03": {"type": "temperature", "location": "room2", "min": 18, "max": 28},
            "device01": {"type": "status", "location": "server_room"},
            "actuator01": {"type": "switch", "location": "light1"}
        }
        self.running = False

    def generateTemperature(self, device):
        baseTemp = random.uniform(device["min"], device["max"])
        # Add some realistic variation
        variation = random.uniform(-0.5, 0.5)
        return round(baseTemp + variation, 2)

    def generateHumidity(self, device):
        baseHumidity = random.uniform(device["min"], device["max"])
        variation = random.uniform(-2, 2)
        return round(baseHumidity + variation, 2)

    def generateStatus(self, device):
        statuses = ["online", "offline", "warning", "error"]
        weights = [0.85, 0.05, 0.07, 0.03]  # Mostly online, sometimes issues
        return random.choices(statuses, weights=weights)[0]

    def generateSwitchState(self, device):
        return random.choice(["ON", "OFF"])

    def simulateDevice(self, deviceId, deviceConfig):
        deviceType = deviceConfig["type"]
        
        if deviceType == "temperature":
            value = self.generateTemperature(deviceConfig)
            topic = f"codePower/sensors/{deviceConfig['location']}/temperature"
            payload = json.dumps({
                "deviceId": deviceId,
                "type": "temperature",
                "value": value,
                "unit": "°C",
                "location": deviceConfig["location"],
                "timestamp": time.time()
            })
            
        elif deviceType == "humidity":
            value = self.generateHumidity(deviceConfig)
            topic = f"codePower/sensors/{deviceConfig['location']}/humidity"
            payload = json.dumps({
                "deviceId": deviceId,
                "type": "humidity",
                "value": value,
                "unit": "%",
                "location": deviceConfig["location"],
                "timestamp": time.time()
            })
            
        elif deviceType == "status":
            value = self.generateStatus(deviceConfig)
            topic = f"codePower/devices/{deviceId}/status"
            payload = json.dumps({
                "deviceId": deviceId,
                "status": value,
                "location": deviceConfig["location"],
                "timestamp": time.time()
            })
            
        elif deviceType == "switch":
            value = self.generateSwitchState(deviceConfig)
            topic = f"codePower/actuators/{deviceConfig['location']}/state"
            payload = json.dumps({
                "deviceId": deviceId,
                "state": value,
                "location": deviceConfig["location"],
                "timestamp": time.time()
            })
        
        return topic, payload

    def startSimulation(self, duration=60, interval=5):
        """Start the device simulation"""
        if not startMqttClient():
            print("Failed to connect to MQTT broker")
            return
        
        print("Device simulator started")
        print(f"Running for {duration} seconds with {interval} second interval")
        print("Press Ctrl+C to stop early")
        
        self.running = True
        startTime = time.time()
        messageCount = 0
        
        try:
            while self.running and (time.time() - startTime) < duration:
                # Simulate each device
                for deviceId, deviceConfig in self.devices.items():
                    topic, payload = self.simulateDevice(deviceId, deviceConfig)
                    
                    if publishMessage(topic, payload):
                        messageCount += 1
                        print(f"Published: {topic} -> {payload}")
                    else:
                        print(f"Failed to publish: {topic}")
                
                # Wait for next interval
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nSimulation stopped by user")
        
        finally:
            self.running = False
            stopMqttClient()
            print(f"Simulation completed. Total messages sent: {messageCount}")

    def stopSimulation(self):
        self.running = False

def quickTest():
    """Quick test with a few messages"""
    simulator = DeviceSimulator()
    
    if startMqttClient():
        time.sleep(2)
        
        print("Publishing quick test messages...")
        
        # Test each device type once
        testDevices = {
            "sensor01": simulator.devices["sensor01"],
            "sensor02": simulator.devices["sensor02"], 
            "device01": simulator.devices["device01"]
        }
        
        for deviceId, deviceConfig in testDevices.items():
            topic, payload = simulator.simulateDevice(deviceId, deviceConfig)
            if publishMessage(topic, payload):
                print(f"✓ {topic} -> {payload}")
            else:
                print(f"✗ Failed: {topic}")
            
            time.sleep(1)
        
        stopMqttClient()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quickTest()
    else:
        # Full simulation
        simulator = DeviceSimulator()
        
        # You can customize duration and interval
        duration = 300  # 5 minutes
        interval = 10   # 10 seconds between device updates
        
        simulator.startSimulation(duration=duration, interval=interval)