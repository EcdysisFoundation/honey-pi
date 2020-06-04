# Hive Pi

## Purpose

Hive Pi is a Raspberry Pi data logging platform designed for the [Ecdysis](<https://www.ecdysis.bio/>) Foundation. It uses MQTT to log different characteristics about each hive.

## Overview

Hive Pi is an MQTT based data logger. Raspberry Pi's powered from PoE hats serve as the main DAQ modules.

![1591223332123](assets/1591223332123.png)

* One Raspberry Pi is used per pallet. 
* Multiple sensors per hive.
* Multiple Pi's per POE Switch.
* One MQTT Broker (Server) 
* One MQTT Data logger and dashboard



## Raspberry Pi Details

The Raspberry Pi's run a python service to collect and submit data to the MQTT server.  It's powered via a PoE shield. This route was chosen so we would not have to worry about servicing batteries or cold weather battery operation problems.

### Sensors

Currently the following sensors are being evaluated:

* Weight - Load Cells in four corners of the hive.
* Temperature - Part of the DHT11 sensor.
* Humidity - Part of the DHT11 sensor.
* Audio - Microphone placed in each hive. Likely only FFT data will be analyzed.

### Wiring & Hardware



### Software

There is one python application (integrated as a service) that controls recording sensor data. It manages sleeping and submits data to the MQTT server using the PAHO library.

Consider using docker / upswift / k8s for rapid deployment. 

Q: How to differentiate between each device? UID ? MAC Address ? File on the SD Card? **TBD**.



## MQTT Server Details

The mqtt server will run the MTIG stack on a Linux system.

* **Mosquitto** MQTT server
* **InfluxDB**  Time series database
* **Telegraf**  Plugin for influxDB to collect MQTT data.
* **Grafana** Data visualization dashboard.

The Linux stack is run in a docker-compose container for quick setup.



## MQTT Data Logging

Hive Pi logs sensor data on a device / pallet / sensor hierarchy. 

Example topics are:

```
/hive-pi/pallet_1/hive_2/temp
                        /humidity
                        /weight
                        /audio
```

And example payload for each topic is:

**Temperature topic data**

```json
{
    "timestamp":1591225410
   	"temp_c":47.3
}
```
**Humidity topic data**
```json
{
    "timestamp":1591225410
   	"humidity_r":0.581
}
```
**Weight topic data**
```json
{
    "timestamp":1591225410
   	"weight_raw":5154
   	"weight_lbs":241.23
}
```
**Audio topic data**

```json
{
    "timestamp":1591225410
   	"filename":"pallet_2_hive_3_1591225410.wav"
   	"blob": "A39jf983fd..."
   	"fft":{
        "freq_range":[1,2,4,2123,24]
        "freq_amp":[22,34,212,541,212]
        "freq_phase_rad":[.23,.341,.214.134]
   	}
}
```





