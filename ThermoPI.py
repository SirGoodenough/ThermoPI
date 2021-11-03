#!/usr/bin/python
# coding: latin-1

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
import json
import requests
import sys
import time
import datetime
import Adafruit_DHT
import yaml
with open("Mysecrets.yml", "r") as ymlfile:
    MYs = yaml.load(ymlfile)

### Paho.mqtt.client
import paho.mqtt.client as mqtt
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.AM2302
# Example of sensor connected to Raspberry Pi pin 23
#DHT_PIN = 23
# Example of sensor connected to Beaglebone Black pin P8_11
#DHT_PIN  = 'P8_11'
DHT_PIN = MYs[PIN]

LWT = MYs[LWT]
FREQUENCY_SECONDS = MYs[LOOP]
HOST = MYs[HOST]
PORT = MYs[PORT]
USER = MYs[USER]
PWD = MYs[PWD]
TEMP_TOPIC = MYs[TEMP]
HUMI_TOPIC = MYs[HUMI]
print('Mosquitto Temp MSG {0}'.format(TEMP_TOPIC))
print('Mosquitto Humidity MSG {0}'.format(HUMI_TOPIC))

    #Log Message to start
print('Logging sensor measurements to {0} every {1} seconds.'.format('Home Assistant', FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
print('Connecting to MQTT on {0}'.format(HOST))
mqttc = client('python_pub', 'False', 'MQTTv311',)
mqttc.username_pw_set(USER, PWD) # deactivate if not needed
mqttc.will_set(LWT, 'Offline', 0, True)
mqttc.connect(HOST, PORT, 60)
mqttc.publish(LWT, 'Online', 0, True)
print('Connecting to MQTT Result: {0} |\|/| {1}'.format(on_connect, on_message))
try:

    while True:
        # Attempt to get sensor reading.
        humidity, tempC = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
        #print 'pass'
        # Skip to the next reading if a valid measurement couldn't be taken.
        # This might happen if the CPU is under a lot of load and the sensor
        # can't be reliably read (timing is critical to read the sensor).
        if humidity is None or tempC is None:
            time.sleep(2)
        continue

        temp = round((9.0/5.0 * tempC + 32),2)  # Conversion to F & round to .2
        humidity = round(humidity,2)            # Round to .2

        currentdate = time.strftime('%Y-%m-%d %H:%M:%S')
        print('Date Time:   {0}'.format(currentdate))
        print('Temperature: {0:0.2f} F'.format(temp))
        print('Humidity:    {0:0.2f} %'.format(humidity))

        # Publish to the MQTT channel
        try:
            mqttc.loop_start()

            print('Updating {0}'.format(TEMP_TOPIC))
            (result1,mid) = mqttc.publish(TEMP_TOPIC,temp,qos=0,retain=True)
            print('Result {0}'.format(on_message))

            print('Updating {0}'.format(HUMI_TOPIC))
            time.sleep(1)
            (result2,mid) = mqttc.publish(HUMI_TOPIC,humidity,qos=0,retain=True)
            print('Result {0}'.format(on_message))

            print('MQTT Updated result {0} and {1}'.format(result1,result2))

            if result1 == 1 or result2 == 1:
                raise ValueError('Result for one message was not 0')
            mqttc.disconnect()

        except Exception as e:
            # Error appending data, most likely because credentials are stale.
            # Null out the worksheet so a login is performed at the top of the loop.
            mqttc.disconnect()
            print('Append error, logging in again: ' + str(e))
            continue

        # Wait 30 seconds before continuing (or your variable setting from command line)
        print('Wrote a message to Home Assistant')
        time.sleep(FREQUENCY_SECONDS)

except Exception as e:
    print('Error connecting to the mqtt server: {0}'.format(e))
