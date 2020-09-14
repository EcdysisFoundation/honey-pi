import json, time, adafruit_dht
import os, pickle

from mqtt.mqtt_setup import mqtt_setup, publish_sensor_data
import RPi.GPIO as GPIO  # import GPIO
from HX711_Python3.hx711 import HX711  # import the class HX711
from statistics import StatisticsError
PALLET = int(os.getenv('PALLET_NUMBER'))
swap_file_name = 'hx711_calibration.swp'

SAMPLE_INTERVAL = 10 * 60 # Seconds
client = mqtt_setup()
hx711_devices = list()


def main():
    # Setup the hx711 sensors
    # Hive, DOUT, SCK
    client.on_message = on_message
    sub_str = "honey_pi/pallet/" + str(PALLET) + "/calibrate/#"
    print("sub_str: ", sub_str)
    client.subscribe(sub_str, qos=1)

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
            try:
                GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
                data_kg = (hx711.get_weight_mean(5))
                data_raw = (hx711.get_raw_data_mean(5))
                # Sucessfully got the data
                sensor_data['timestamp'] = int(round(time.time() * 1000))
                sensor_data['weight_raw'] = data_raw
                sensor_data['weight_cal_kg'] = data_kg
                sensor_data['pallet'] = int(PALLET)
                sensor_data['hive_local'] = int(hive)
                sensor_data['hive_global'] = ((PALLET - 1)*4) + int(hive)
                publish_sensor_data("honey_pi/pallet/" + str(PALLET) + "/hive/" + hive + "/hx711", sensor_data)
                break  # This attempt was successful, onto the next sensor
            except Exception as e:
                # This attempt wasn't successful. Log the warning.
                publish_sensor_data("honey_pi/warnings/pallet/hx711/" + str(PALLET), str(e) + " hive: " + str(hive))
                break # onto the next sensor


def startup():
    global hx711_devices
    # This will be ignored if there is a swap file.
    hx711_sensors = (("1", 5, 6),
                     ("2", 16, 6),
                     ("3", 26, 6),
                     ("4", 25, 6)
                     )
    print("startup")
    for hive, dout, sck in hx711_sensors:
        try:
            hx_device = HX711(dout_pin=dout, pd_sck_pin=sck)
            hx711_devices.append((hive, hx_device))

        except Exception as e:
            publish_sensor_data("honey_pi/errors/pallet/" + str(PALLET), "Could not configure the hx711 device")
            publish_sensor_data("honey_pi/errors/pallet/" + str(PALLET), str(e) + "hive: " + str(hive) )

    print("startup: checking for swap file")
    # Check if we have swap file (calibration) if not, we do not have any calibration.
    if os.path.isfile(swap_file_name):
        print('calibration file found')
        with open(swap_file_name, 'rb') as swap_file:
            hx711_devices = pickle.load(swap_file)
            # now we loaded the state before the Pi restarted.
    else:
        print("startup: No swap file")
        # There is no swap file. Push an error.
        publish_sensor_data("honey_pi/errors/pallet/" + str(PALLET), "No swap file found on startup.")


def calibrate_zero_weight(hive_num):
    # This routine is called when we receive a message from
    # honey_pi/PALLET/calibrate/tare
    try:
        hive, hx = hx711_devices[int(hive_num-1)]
        err = hx.zero()
        if err:
            print('Tare is unsuccessful for hive ' + str(hive_num))
    except Exception as e:
        publish_sensor_data("honey_pi/errors/pallet/" + str(PALLET), str(e) + " hive: " + str(hive_num))


def calibrate_known_weight(weight_kg, hive_num):
    # after calibrating the known weight, save the swap file.
    # Then reload the 'startup' routine to set the file appropriately.
    # honey_pi/PALLET/calibrate/weight --> weight
    try:
        hive, hx = hx711_devices[int(hive_num-1)]
        reading = hx.get_data_mean(5)
        ratio = reading / weight_kg
        hx.set_scale_ratio(ratio)
        print('Saving the HX711 state to swap file on persistent memory')
        with open(swap_file_name, 'wb') as swap_file:
            pickle.dump(hx711_devices, swap_file)
            swap_file.flush()
            os.fsync(swap_file.fileno())
            # you have to flush, fsynch and close the file all the time.
            # This will write the file to the drive. It is slow but safe.
        print('about to execute startup from cal weight')
        startup()
        publish_sensor_data("honey_pi/notifications/pallet/"+str(PALLET)+"/", "Successfully calibrated hive: " + str(hive_num))
        print("notification sent")

    except Exception as e:
        print('failed to calibrate')
        publish_sensor_data("honey_pi/errors/pallet/" + str(PALLET), str(e) + " hive: " + str(hive_num))


def on_message(client, userdata, msg):
    print("new message")
    try:
        if msg.topic == "honey_pi/pallet/" + str(PALLET) + "/calibrate/tare":
            print("zero message received")
            payload = msg.payload.decode("utf-8")
            calibrate_zero_weight(int(payload))
        elif msg.topic == "honey_pi/pallet/" + str(PALLET) + "/calibrate/weight":
            print("weight_kg message received")
            try:
                payload = msg.payload.decode("utf-8")
                hive_num, weight = payload.split(",")
                hive_num = int(hive_num)
                weight = int(weight)
                calibrate_known_weight(weight_kg=weight, hive_num=hive_num)
                print("weight_kg complete")
            except Exception as e:
                print("calibration error")
                publish_sensor_data("honey_pi/errors/pallet/" + str(PALLET), str(e))
                publish_sensor_data("honey_pi/errors/pallet/" + str(PALLET), "calibration payload likely missing weight and hive")
        else:
            print("unknown message topic")

    except Exception as e:
        publish_sensor_data("honey_pi/errors/pallet/" + str(PALLET), str(e))


if __name__ == '__main__':
    # Check if the PALLET var has been set
    _ = int(PALLET)
    print("starting main")
    main()

