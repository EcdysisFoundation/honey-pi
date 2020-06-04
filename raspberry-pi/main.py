import paho.mqtt.client as mqtt #import the MQTT library
import json, time
import Adafruit_DHT as dht


ACCESS_TOKEN = ""
MQTT_BROKER = 'test.mosquitto.org'
MQTT_PORT = 1883
SAMPLE_INTERVAL = 2  # seconds

class HiveMonitor:
    client = None

    def __init__(self):
        self.client = mqtt.Client()

        if ACCESS_TOKEN:
            self.client.username_pw_set(ACCESS_TOKEN)

        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()

        self.client.publish("AC_unit", "on")
        time.sleep(1)

    def sample_loop(self):
        next_reading = time.time()
        while True:
            self.publish_sensor_data()
            next_reading += SAMPLE_INTERVAL
            sleep_time = next_reading-time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.publish_sensor_data()

    def publish_sensor_data(self):
        humidity, temperature = [2,3]
        #humidity, temperature = dht.read_retry(dht.DHT22,4)

        sensor_data = dict()
        sensor_data['timestamp'] = int(round(time.time() * 1000))
        sensor_data['temperature_c'] = temperature

        self.client.publish("hive_monitor/pallet_1/hive_1/temp", json.dumps(sensor_data), qos=2)


