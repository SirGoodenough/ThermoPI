#!/usr/bin/python3

# ThermoPI has been assembled by Sir GoodEnough (Jim Chaloupka)
#  from the knowledge gained from others.
#  Use of this program is free to makers of non commercial uses & 
#  also within the license of other packages relied upon herein.
#

# DHT Sensor Data-logging to MQTT Temperature channel

# Requies a Mosquitto Server Install On the destination.

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
# MQTT Encahncements: David Cole (2016)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import Adafruit_DHT
import datetime
import io
import paho.mqtt.client as mqtt
import requests
import sys
import time
import yaml
import json

#  Get the parameter file
with open("/opt/ThermoPI/MYsecrets.yaml", "r") as ymlfile:
    MYs = yaml.safe_load(ymlfile)

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.AM2302
# Example of sensor connected to Raspberry Pi pin 23
#DHT_PIN = 23
# Example of sensor connected to Beaglebone Black pin P8_11
#DHT_PIN  = 'P8_11'
DHT_PIN = MYs["PIN"]
LOOP = MYs["LOOP"]
HOST = MYs["HOST"]
PORT = MYs["PORT"]
USER = MYs["USER"]
PWD = MYs["PWD"]
STATE = MYs["STATE"]
DEVICE = MYs["DEVICE"]
LWT = MYs["LWT"]

NAMEH = MYs["NAMEH"]
H_ID = MYs["H_ID"]
CONFIGH = MYs["CONFIGH"]

NAMET = MYs["NAMET"]
T_ID = MYs["T_ID"]
CONFIGT = MYs["CONFIGT"]

payloadHconfig = {
    "name":NAMEH,
    "dev_cla":"humidity",
    "stat_t":STATE,
    "avty_t":LWT,
    "pl_avail":"Online",
    "pl_not_avail":"Offline",
    "unit_of_meas":"%",
    "val_tpl":"{{ value_json.humidity }}" }

payloadTconfig = {
    "name":NAMET,
    "dev_cla":"temperature",
    "stat_t":STATE,
    "avty_t":LWT,
    "pl_avail":"Online",
    "pl_not_avail":"Offline",
    "unit_of_meas":"°F",
    "val_tpl":"{{ value_json.temperature }}" }

def mqttConnect():
    print('Connecting to MQTT on {0} {1}'.format(HOST,PORT))
    mqttc.connect(HOST, PORT, 60)
    mqttc.loop_start()
    mqttc.will_set(LWT, 'Online', 1, True)
    mqttc.publish(CONFIGH, json.dumps(payloadHconfig), 1, True)
    mqttc.publish(CONFIGT, json.dumps(payloadTconfig), 1, True)

print('Mosquitto STATE topic {0}'.format(STATE))

    #Log Message to start
print('Logging sensor measurements from {0} & {1} every {2} seconds.'.format(NAMET, NAMEH, LOOP))
print('Press Ctrl-C to quit.')
mqttc = mqtt.Client('python_pub', 'False', 'MQTTv311',)
mqttc.username_pw_set(USER, PWD) # deactivate if not needed
mqttConnect()

try:

    while True:
        # Attempt to get sensor reading.
        humidity, tempC = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN)

        tempF = round((9.0/5.0 * tempC + 32),1) # Conversion to F & round to .1
        humidityOut = round(humidity,1)         # Round to .1

        currentdate = time.strftime('%Y-%m-%d %H:%M:%S')
        print('Date Time:   {0}'.format(currentdate))

        # Publish to MQTT
        try:
            payloadOut = {
                "temperature": tempF,
                "humidity": humidityOut}
            print('Updating {0} {1}'.format(STATE,json.dumps(payloadOut) ) )
            (result1,mid) = mqttc.publish(STATE, json.dumps(payloadOut), 1, True)

            print('MQTT Update result {0}'.format(result1))

            if result1 == 1:
                raise ValueError('Result message from MQTT was not 0')

        except Exception as e:
            # Error appending data, most likely because credentials are stale.
            #  disconnect and re-connect...
            print('MQTT error, trying re-connect: ' + str(e))
            mqttc.will_set(LWT, 'Offline', 0, True)
            mqttc.loop_stop()
            mqttc.disconnect()
            time.sleep(1)
            mqttConnect()

            continue

        # Wait before continuing (your variable setting 'LOOP')
        print('Sent values to Home Assistant')
        time.sleep(LOOP)

except KeyboardInterrupt:
    print('Keyboard Interrupt')
    # mqttc.will_set(LWT, 'offline', 0, True)
    mqttc.loop_stop()
    mqttc.will_set(LWT, 'Offline', 1, True)
    mqttc.disconnect()
    sys.exit()
