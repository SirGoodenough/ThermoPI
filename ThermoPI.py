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
import paho.mqtt.client as mqtt
import sys
import time
import yaml
import json
import uuid

#  Get the parameter file
with open("/opt/ThermoPI/MYsecrets.yaml", "r") as ymlfile:
    MYs = yaml.safe_load(ymlfile)

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302
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
AREA = MYs["AREA"]

# Pulling the unique MAC SN section address using uuid and getnode() function 
DEVICE_ID = (hex(uuid.getnode())[-6:]).upper()

TOPIC = "homeassistant/sensor/"

NAMED = MYs["DEVICE_NAME"]
D_ID = DEVICE_ID + '_' + NAMED
STATE = TOPIC + D_ID + '/state'
LWT = TOPIC + D_ID + '/lwt'

NAMEH = MYs["NAMEH"]
H_ID =  DEVICE_ID + '_' + MYs["H_ID"]
CONFIGH = TOPIC + H_ID + '/config'

NAMET = MYs["NAMET"]
T_ID = DEVICE_ID + '_' + MYs["T_ID"]
CONFIGT = TOPIC + T_ID + '/config'

payloadHconfig = {
    "name": NAMEH,
    "stat_t": STATE,
    "avty_t": LWT,
    "pl_avail": "Online",
    "pl_not_avail": "Offline",
    "uniq_id": H_ID,
    "dev": {
        "ids": [
        D_ID,
        DEVICE_ID
        ],
        "name": "ThermoPI",
        'sa': AREA,
        "mf": "SirGoodenough",
        "mdl": "HomeAssistant Discovery for ThermoPI",
        "sw": "https://github.com/SirGoodenough/ThermoPI"
    },
    "unit_of_meas": "%",
    "dev_cla":"humidity",
    "frc_upd": True,
    "val_tpl": "{{ value_json.humidity }}"
}

payloadTconfig = {
    "name": NAMET,
    "stat_t": STATE,
    "avty_t": LWT,
    "pl_avail": "Online",
    "pl_not_avail": "Offline",
    "uniq_id": T_ID,
    "dev": {
        "ids": [
        D_ID,
        DEVICE_ID
        ],
        "name": "ThermoPI",
        'sa': AREA,
        "mf": "SirGoodenough",
        "mdl": "HomeAssistant Discovery for ThermoPI",
        "sw": "https://github.com/SirGoodenough/ThermoPI"
    },
    "unit_of_meas":"°F",
    "dev_cla":"temperature",
    "frc_upd": True,
    "val_tpl": "{{ value_json.temperature }}"
}

def mqttConnect():
    print('Connecting to MQTT on {0} {1}'.format(HOST,PORT))
    mqttc.connect(HOST, PORT, 60)
    mqttc.loop_start()
    mqttc.publish(LWT, "Online", 1, True)
    mqttc.publish(CONFIGH, json.dumps(payloadHconfig), 1, True)
    mqttc.publish(CONFIGT, json.dumps(payloadTconfig), 1, True)

print('Mosquitto STATE topic {0}'.format(STATE))

    #Log Message to start
print('Logging sensor measurements from {0} & {1} every {2} seconds.'.format(NAMET, NAMEH, LOOP))
print('Press Ctrl-C to quit.')
mqttc = mqtt.Client(D_ID, 'False', 'MQTTv311',)
mqttc.disable_logger()   # Saves wear on SD card Memory.  Remove as needed for troubleshooting
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
            mqttc.publish(LWT, 'Offline', 0, True)
            time.sleep(2)
            mqttc.loop_stop()
            mqttc.disconnect()
            time.sleep(1)
            mqttConnect()
            pass

            continue

        # Wait before continuing (your variable setting 'LOOP')
        print('Sent values to Home Assistant')
        time.sleep(LOOP)

except KeyboardInterrupt:
    print(' Keyboard Interrupt. Closing MQTT.')
    mqttc.publish(LWT, 'Offline', 1, True)
    time.sleep(1)
    mqttc.loop_stop()
    mqttc.disconnect()
    sys.exit()
