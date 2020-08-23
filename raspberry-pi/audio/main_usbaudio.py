import json, time, board, adafruit_dht
from mqtt.mqtt_setup import mqtt_setup, publish_sensor_data
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
import os
PALLET = int(os.getenv('PALLET_NUMBER'))

FS = 44100               # Sample rate frequency
REC_TIME = 2 #30            # Seconds
SAMPLE_INTERVAL = 5 # 20*60  # Seconds

client = mqtt_setup()
dht_devices = list()
microphones = ()


def main():
    # Setup the microphones
    # Hive number, USB device number
    global microphones
    microphones = (("1", 0),
                   ("2", 1),
                   ("3", 2),
                   ("4", 3))

    next_reading = time.time()
    while True:
        next_reading += SAMPLE_INTERVAL
        sleep_time = next_reading - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        read_sensor()


def read_sensor():
    print("Reading Sensor")
    for hive, microphone in microphones:
        sensor_data = dict()
        try:
            sd.default.device = microphone
            sd.default.samplerate = FS
            recording = sd.rec(int(REC_TIME * FS), channels=1, blocking=True)

            N = recording.shape[0]
            L = N / FS
            tuckey_window = signal.tukey(N, 0.01, True)  # generate the Tuckey window, widely open, alpha=0.01
            ysc = recording[:, 0] * tuckey_window        # applying the Tuckey window
            yk = np.fft.rfft(ysc, int(2500 * L * 2))     # real to complex DFT
            k = np.arange(yk.shape[0])
            freqs = k / L
            amps = np.abs(yk)

            sensor_data['timestamp'] = int(round(time.time() * 1000))
            sensor_data['frequencies'] = freqs.tolist()
            sensor_data['amplitudes'] = amps.tolist()
            sensor_data['hive_local'] = int(hive)
            sensor_data['hive_global'] = ((PALLET - 1) * 4) + int(hive)
            sensor_data['pallet'] = PALLET

        except Exception as e:
            print("Error with microphone")
            publish_sensor_data("honey_pi/errors/pallet/" + str(PALLET), str(e) + " hive: " + str(hive))

        publish_sensor_data("honey_pi/pallet/" + str(PALLET) + "/hive/" + hive + "/audio", sensor_data)


if __name__ == '__main__':
    # Check if the PALLET var has been set
    _ = int(PALLET)
    main()
