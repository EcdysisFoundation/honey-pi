import json, time, board, adafruit_dht
import os, pickle
from mqtt.mqtt_setup import mqtt_setup, publish_sensor_data
import RPi.GPIO as GPIO  # import GPIO
from HX711_Python3.hx711 import HX711  # import the class HX711

PALLET = os.getenv('PALLET_NUMBER')

SAMPLE_INTERVAL = 2
client = mqtt_setup()
hx711_devices = list()


def main():
    # Setup the hx711 sensors
    # Hive, DOUT, SCK
    startup()

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
    sensor_data['pallet'] = PALLET

    for hive, dout, sck in hx711_sensors:
        sensor_data = dict()
        for attempt in range(10):
            error_log = list()
            try:
                GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
                hx = HX711(dout_pin=dout, pd_sck_pin=sck)
                data = (hx.get_raw_data_mean())
                GPIO.cleanup()  # clean up any ports I'm using in this program

            except RuntimeError as error:
                error_log.append(error.args[0])
            else:
                # Sucessfully got the data
                sensor_data['timestamp'] = int(round(time.time() * 1000))
                sensor_data['weight_raw'] = data
                sensor_data['weight_cal'] =
                sensor_data['pallet'] = PALLET
                sensor_data['hive_local'] = hive
                sensor_data['hive_global'] = ((PALLET - 1)*4) + hive

                publish_sensor_data("honey_pi/hx711", sensor_data)
                break
        else:
            # we failed all the attempts - deal with the consequencs
            publish_sensor_data("honey_pi/errors/hive"+hive, error_log)


def startup():
    global hx711_sensors
    hx711_sensors = (("1", 5, 6),
                     ("2", 5, 6),
                     ("3", 5, 6),
                     ("4", 5, 6))
    global hx711_devices
    for hive, dout, sck in hx711_sensors:
        hx_device = HX711(dout_pin=dout, pd_sck_pin=sck)
        hx711_devices.append((hive, hx_device))

    # Check if we have swap file (calibration) if not, we do not have any calibration.
    swap_file_name = 'hx711_calibration.swp'
    if os.path.isfile(swap_file_name):
        with open(swap_file_name, 'rb') as swap_file:
            hx711_sensors = pickle.load(swap_file)
            # now we loaded the state before the Pi restarted.
    else:
        # There is no swap file. Push an error.
        error_data = dict()
        error_data['pallet'] = PALLET
        error_data['sensor'] = 'hx711'
        error_data['message'] = 'There is no calibration file available for the hx711 sensor!'
        publish_sensor_data("honey_pi/errors", error_data)


def calibrate_zero_weight():
    # This routine is called when we receive a message from
    # honey_pi/hx711/calibrate/PALLET/
    pass

def calibrate_known_weight():
    # after calibrating the known weight, save the swap file.
    # Then reload the 'startup' routine to set the file approperately.



if __name__ == '__main__':
    main()




