import json, time, board, adafruit_dht
from mqtt.mqtt_setup import mqtt_setup, publish_sensor_data

import os
PALLET = int(os.getenv('PALLET_NUMBER'))

SAMPLE_INTERVAL = 10 * 60
client = mqtt_setup()
dht_devices = list()


def main():
    # Setup the DHT11 sensors
    sensors = (("1", board.D27),
               ("2", board.D17),
               ("3", board.D22),
               ("4", board.D23),
               )
    global dht_devices
    for hive, sensor in sensors:
        try:
            dht_device = adafruit_dht.DHT11(sensor)
            dht_devices.append( (hive,dht_device) )
        except Exception as e:
            print("Error initializing dht11 sensor " + hive)
            publish_sensor_data("honey_pi/errors/pallet/" + str(PALLET),  str(repr(e)) + "hive: " + str(hive) )

    next_reading = time.time()
    while True:
        next_reading += SAMPLE_INTERVAL
        sleep_time = next_reading - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        read_sensor()


def read_sensor():
    for hive, dht_device in dht_devices:
        sensor_data = dict()
        for attempt in range(10):
            try:
                temp_c = dht_device.temperature
                humid_r = dht_device.humidity
                # Sucessfully got the data
                sensor_data['timestamp'] = int(round(time.time() * 1000))
                sensor_data['temperature_c'] = temp_c * 1.0
                sensor_data['humidity_r'] = humid_r
                sensor_data['hive_local'] = int(hive)
                sensor_data['hive_global'] = ((PALLET - 1)*4) + int(hive)
                sensor_data['pallet'] = PALLET
                publish_sensor_data("honey_pi/pallet/" + str(PALLET) + "/hive/" + hive + "/dht11", sensor_data)
                break  # Completed this attempt successfully, go onto the next sensor
            except Exception as e:
                publish_sensor_data("honey_pi/warnings/pallet/" + str(PALLET), str(repr(e)) + "hive: " + str(hive))
                break




if __name__ == '__main__':
    # Check if the PALLET var has been set
    _ = int(PALLET)
    main()
