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
LWT = MYs["LWT"]
LOOP = MYs["LOOP"]
HOST = MYs["HOST"]
PORT = MYs["PORT"]
USER = MYs["USER"]
PWD = MYs["PWD"]
TEMP_TOPIC = MYs["TEMP"]
HUMI_TOPIC = MYs["HUMI"]
print('Mosquitto Temp topic {0}'.format(TEMP_TOPIC))
print('Mosquitto Humidity topic {0}'.format(HUMI_TOPIC))

    #Log Message to start
print('Logging sensor measurements to {0} every {1} seconds.'.format('Home Assistant', LOOP))
print('Press Ctrl-C to quit.')
print('Connecting to MQTT on {0}'.format(HOST))
mqttc = mqtt.Client('python_pub', 'False', 'MQTTv311',)
mqttc.username_pw_set(USER, PWD) # deactivate if not needed
mqttc.will_set(LWT, 'Offline', 0, True)
try:

    while True:
        # Attempt to get sensor reading.
        humidity, tempC = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN)

        temp = round((9.0/5.0 * tempC + 32),1)  # Conversion to F & round to .1
        humidity = round(humidity,1)            # Round to .1

        currentdate = time.strftime('%Y-%m-%d %H:%M:%S')
        print('Date Time:   {0}'.format(currentdate))
        print('Temperature: {0:0.1f} F'.format(temp))
        print('Humidity:    {0:0.1f} %'.format(humidity))

        # Publish to the MQTT channel
        try:
            mqttc.connect(HOST, PORT, 60)
            # mqttc.publish(LWT, 'Online', 0, True)

            print('Updating {0}'.format(TEMP_TOPIC))
            (result1,mid) = mqttc.publish(TEMP_TOPIC,temp,qos=0,retain=True)
        
            print('Updating {0}'.format(HUMI_TOPIC))
            time.sleep(1)
            (result2,mid) = mqttc.publish(HUMI_TOPIC,humidity,qos=0,retain=True)
    
            print('MQTT Updated result {0} and {1}'.format(result1,result2))

            if result1 == 1 or result2 == 1:
                raise ValueError('Result for one message was not 0')
            mqttc.disconnect()

        except Exception as e:
            # Error appending data, most likely because credentials are stale.
            # Null out the worksheet so a login is performed at the top of the loop.
            mqttc.publish(LWT, 'Offline', 0, True)
            mqttc.disconnect()
            print('Append error, logging in again: ' + str(e))
            continue

        # Wait 30 seconds before continuing (or your variable setting from command line)
        print('Wrote a message to Home Assistant')
        time.sleep(LOOP)

except Exception as e:
    mqttc.publish(LWT, 'Offline', 0, True)
    print('Error connecting to the mqtt server: {0}'.format(e))
