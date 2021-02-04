#!/usr/bin/python

# ThermoPI has been assembled by Sir GoodEnough (Jim Chaloupka)
#  from the knowledge gained from others.
#  Use of this program is free to makers of non commercial uses 
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
import paho.mqtt.client as mqtt
import Adafruit_DHT


#==================================================================================================================================================
#Usage
#python mqtt.channel.py <temp topic> <humidity topic> <gpio pin> <optional update frequency>
# eg python mqtt.channel.py 'cupboard/temperature1' 'cupboard/humidity1' 4
# will start an instance using 'cupboard/temperature1' as the temperature topic, and using gpio port 4 to talk to a DHT22 sensor
# it will use the default update time of 300 secons.
#==================================================================================================================================================

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.AM2302

# Example of sensor connected to Raspberry Pi pin 23
DHT_PIN  = sys.argv[3]
# Example of sensor connected to Beaglebone Black pin P8_11
#DHT_PIN  = 'P8_11'

if (len(sys.argv) < 2):
   raise  ValueError('Input arguments of mqtt channel temperature humidity not passed')

MOSQUITTO_HOST = '10.10.78.10' #Your Broker IP Address Here
MOSQUITTO_PORT = 1883  #Your MQTT Port Here
MOSQUITTO_USER = 'MQTTLogin' #change to your credentials as needed
MOSQUITTO_PWD  = '78686a83-ab00-4bbe-8f86-b3be9eaa844a'
MOSQUITTO_TEMP_MSG = str(sys.argv[1]) # Old channel name in here
MOSQUITTO_HUMI_MSG = str(sys.argv[2]) # Old channel name now passed by argument
print('Mosquitto Temp MSG {0}'.format(MOSQUITTO_TEMP_MSG))
print('Mosquitto Humidity MSG {0}'.format(MOSQUITTO_HUMI_MSG))

# How long to wait (in seconds) between measurements.
print "Args length: " + str(len(sys.argv))
FREQUENCY_SECONDS      = 300

if (len(sys.argv) > 4):
    FREQUENCY_SECONDS = float(sys.argv[4])

    #Log Message to start
print('Logging sensor measurements to {0} every {1} seconds.'.format('MQTT', FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
print('Connecting to MQTT on {0}'.format(MOSQUITTO_HOST))
mqttc = mqtt.Client("python_pub",transport='websockets')
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
        mqttc.username_pw_set(MOSQUITTO_USER,MOSQUITTO_PWD) # deactivate if not needed
        try:
            mqttc.connect(MOSQUITTO_HOST,MOSQUITTO_PORT);
            print 'Updating {0}'.format(MOSQUITTO_TEMP_MSG)
            (result1,mid) = mqttc.publish(MOSQUITTO_TEMP_MSG,temp,qos=0,retain=True)
            print 'Updating {0}'.format(MOSQUITTO_HUMI_MSG)
            time.sleep(1)
            (result2,mid) = mqttc.publish(MOSQUITTO_HUMI_MSG,humidity,qos=0,retain=True)
            print 'MQTT Updated result {0} and {1}'.format(result1,result2)
            if result1 == 1 or result2 == 1:
                raise ValueError('Result for one message was not 0')
            mqttc.disconnect()

        except Exception,e:
            # Error appending data, most likely because credentials are stale.
            # Null out the worksheet so a login is performed at the top of the loop.
            mqttc.disconnect()
            print('Append error, logging in again: ' + str(e))
            continue

        # Wait 30 seconds before continuing (or your variable setting from command line)
        print('Wrote a message to MQTT')
        time.sleep(FREQUENCY_SECONDS)

except Exception as e:
    print('Error connecting to the mqtt server: {0}'.format(e))

