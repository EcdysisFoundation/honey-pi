import json, time, board, adafruit_dht
from mqtt.mqtt_setup import mqtt_setup, publish_sensor_data

SAMPLE_INTERVAL = 2
client = mqtt_setup()
dht_devices = list()


def main():
    # Setup the DHT11 sensors
    sensors = (("1", board.D27),
               ("2", board.D17),
               ("3", board.D22),
               ("4", board.D23))
    global dht_devices
    for hive, sensor in sensors:
        dht_device = adafruit_dht.DHT11(sensor)
        dht_devices.append( (hive,dht_device) )

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
            error_log = list()
            try:
                temp_c = dht_device.temperature
                humid_r = dht_device.humidity
            except RuntimeError as error:
                error_log.append(error.args[0])
            else:
                # Sucessfully got the data
                sensor_data['timestamp'] = int(round(time.time() * 1000))
                sensor_data['temperature_c'] = temp_c * 1.0
                sensor_data['humidity_r'] = humid_r
                sensor_data['hive'] = hive
                sensor_data['pallet'] = 100
                publish_sensor_data("honey_pi/dht11", sensor_data)
                break
        else:
            # we failed all the attempts - deal with the consequencs
            publish_sensor_data("honey_pi/errors/hive"+hive,error_log)

if __name__ == '__main__':
    main()




