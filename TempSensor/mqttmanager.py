# mqttmanager.py

from umqttsimple import MQTTClient
import config

class MQTTManager:
    def __init__(self, mqtt_server, mqtt_port=1883, mqtt_user=None, mqtt_password=None, status_topic='sensor'):
        self.mqtt_server = mqtt_server
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.status_topic = status_topic
        self.client = None
        self.is_connected = False

    async def connect(self):
        try:
            self.client = MQTTClient(
                client_id=str(config.SENSOR_ID),  # set in config.py
                server=self.mqtt_server,
                port=self.mqtt_port,
                user=self.mqtt_user,
                password=self.mqtt_password
            )
            self.client.set_last_will(
                f"{self.status_topic}/{config.SENSOR_ID}/status",
                "disconnected",
                retain=True
            )
            self.client.connect()
            self.is_connected = True
            print(f"Connected to MQTT broker at {self.mqtt_server}")
            
            self.client.publish(
                f"{self.status_topic}/{config.SENSOR_ID}/status",
                "connected",
                retain=True
            )
            
            return True
        
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
        self.is_connected = False

    def publish(self, topic, message):
        if self.is_connected:
            try:
                self.client.publish(topic, message)
                return True
            except Exception as e:
                print(f"Failed to publish MQTT message: {e}")
                self.is_connected = False
                return False
        return False
