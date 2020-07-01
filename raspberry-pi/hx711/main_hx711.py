import json, time, board, adafruit_dht
import os, pickle
import traceback

from mqtt.mqtt_setup import mqtt_setup, publish_sensor_data
import RPi.GPIO as GPIO  # import GPIO
from HX711_Python3.hx711 import HX711  # import the class HX711
from statistics import StatisticsError
PALLET = int(os.getenv('PALLET_NUMBER'))
swap_file_name = 'hx711_calibration.swp'

SAMPLE_INTERVAL = 2
client = mqtt_setup()
hx711_devices = list()


def main():
    # Setup the hx711 sensors
    # Hive, DOUT, SCK
    client.on_message = on_message
    client.subscribe("honey_pi/hx711/calibrate/#", qos=1)

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

    for hive, hx711 in hx711_devices:
        for attempt in range(10):
            error_log = list()
            try:
                GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
                data_kg = (hx711.get_weight_mean(5))
                data_raw = (hx711.get_raw_data_mean(5))

            except RuntimeError as error:
                error_log.append(error.args[0])
            except StatisticsError as error:
                print("Could not get data for hive number " + str(hive))
                error_log.append(error.args[0])
            else:
                # Sucessfully got the data
                sensor_data['timestamp'] = int(round(time.time() * 1000))
                sensor_data['weight_raw'] = data_raw
                sensor_data['weight_cal_kg'] = data_kg
                sensor_data['pallet'] = PALLET
                sensor_data['hive_local'] = int(hive)
                sensor_data['hive_global'] = ((PALLET - 1)*4) + int(hive)

                publish_sensor_data("honey_pi/hx711", sensor_data)
                break
        else:
            # we failed all the attempts - deal with the consequencs
            publish_sensor_data("honey_pi/errors/hive"+hive, error_log)


def startup():
    global hx711_devices
    # This will be ignored if there is a swap file.
    hx711_sensors = (("1", 5, 6),
                     ("2", 16, 6),
                     ("3", 26, 6),
                    # ("4", 25, 6)
                     )

    for hive, dout, sck in hx711_sensors:
        hx_device = HX711(dout_pin=dout, pd_sck_pin=sck)
        hx711_devices.append((hive, hx_device))

    # Check if we have swap file (calibration) if not, we do not have any calibration.
    if os.path.isfile(swap_file_name):
        print('calibration file found')
        with open(swap_file_name, 'rb') as swap_file:
            hx711_devices = pickle.load(swap_file)
            # now we loaded the state before the Pi restarted.
    else:
        # There is no swap file. Push an error.
        error_data = dict()
        error_data['pallet'] = PALLET
        error_data['sensor'] = 'hx711'
        error_data['message'] = 'There is no calibration file available for the hx711 sensor!'
        publish_sensor_data("honey_pi/errors", error_data)



def calibrate_zero_weight(hive_num):
    # This routine is called when we receive a message from
    # honey_pi/hx711/calibrate/PALLET/zero
    #for hive, hx in hx711_devices:
    #    err = hx.zero()
    #    if err:
    #        raise print('Tare is unsuccessful.')
    hive, hx =  hx711_devices[int(hive_num)]
    err = hx.zero()
    if err:
        raise print('Tare is unsucessful for hive' + str(hive_num))

def calibrate_known_weight(weight_kg, hive_num):
    # after calibrating the known weight, save the swap file.
    # Then reload the 'startup' routine to set the file appropriately.
    # honey/pi/hx711/calibrate/pallet/weight --> weight
    #for hive, hx in hx711_devices:
    #    reading = hx.get_data_mean(1)
    #    ratio = reading / weight_kg
    #    hx.set_scale_ratio(ratio)
    

    print('Saving the HX711 state to swap file on persistant memory')
    with open(swap_file_name, 'wb') as swap_file:
        pickle.dump(hx711_devices, swap_file)
        swap_file.flush()
        os.fsync(swap_file.fileno())
        # you have to flush, fsynch and close the file all the time.
        # This will write the file to the drive. It is slow but safe.
    print('startup')
    startup()


def on_message(client, userdata, msg):
    try:
        if msg.topic == "honey_pi/hx711/calibrate/pallet/" + str(PALLET) + "/zero":
            print("zero message received")
            calibrate_zero_weight(int(msg.payload))
        elif msg.topic == "honey_pi/hx711/calibrate/pallet/" + str(PALLET) + "/weight_kg":
            print("weight_kg message received")
            hive_num = int(msg.payload)
            calibrate_known_weight(32, hive_num)
            print("weight_kg complete")
        else:
            #ignore
            pass
    except:
        traceback.print_exc()
        quit(0)


if __name__ == '__main__':
    main()




