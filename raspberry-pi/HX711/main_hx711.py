import json, time, board, adafruit_dht
from mqtt.mqtt_setup import mqtt_setup, publish_sensor_data
import RPi.GPIO as GPIO  # import GPIO
from HX711_Python3.hx711 import HX711  # import the class HX711

SAMPLE_INTERVAL = 2
client = mqtt_setup()
dht_devices = list()


def main():

    next_reading = time.time()
    while True:
        next_reading += SAMPLE_INTERVAL
        sleep_time = next_reading - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        read_sensor()


def read_sensor():
    sensor_data = dict()
    sensor_data['timestamp'] = int(round(time.time() * 1000))
    sensor_data['pallet'] = 100



    GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
    hx = HX711(dout_pin=5, pd_sck_pin=6)  # create an object
    data = (hx.get_raw_data_mean())  # get raw data reading from hx711
    GPIO.cleanup()

    sensor_data['weight_raw'] = data

    publish_sensor_data("honey_pi/hx711", sensor_data)


    # for hive, dht_device in dht_devices:
    #     sensor_data = dict()
    #     for attempt in range(10):
    #         error_log = list()
    #         try:
    #             temp_c = dht_device.temperature
    #             humid_r = dht_device.humidity
    #         except RuntimeError as error:
    #             error_log.append(error.args[0])
    #         else:
    #             # Sucessfully got the data
    #             sensor_data['timestamp'] = int(round(time.time() * 1000))
    #             sensor_data['temperature_c'] = temp_c * 1.0
    #             sensor_data['humidity_r'] = humid_r
    #             sensor_data['hive'] = hive
    #             sensor_data['pallet'] = 100
    #             publish_sensor_data("honey_pi/dht11", sensor_data)
    #             break
    #     else:
    #         # we failed all the attempts - deal with the consequencs
    #         publish_sensor_data("honey_pi/errors/hive"+hive, error_log)


if __name__ == '__main__':
    main()




