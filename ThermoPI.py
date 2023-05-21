#!/usr/bin/python3

# ThermoPI has been assembled by Sir GoodEnough (Jim Chaloupka)
#  from the knowledge gained from others.
#  Use of this program is free to makers of non commercial uses & 
#  also within the license of other packages relied upon herein.
#

# DHT Sensor Data-logging to MQTT Temperature channel

# Requires a Mosquitto Server Install On the destination.

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
# MQTT Enhancements: David Cole (2016)

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
import RPi.GPIO as GPIO

#  Get the parameter file
with open("/opt/ThermoPI/MYsecrets.yaml", "r") as ymlfile:
    MYs = yaml.safe_load(ymlfile)

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302
DHT_TYPE = Adafruit_DHT.AM2302
# Example of sensor connected to Raspberry Pi pin 23
#DHT_PIN = 23
# Example of sensor connected to Beaglebone Black pin P8_11
#DHT_PIN  = 'P8_11'
DHT_PIN = MYs["TEMP"]["PIN"]
AREA = MYs["TEMP"]["AREA"]

LOOP = MYs["MAIN"]["LOOP"]
HOST = MYs["MAIN"]["HOST"]
PORT = MYs["MAIN"]["PORT"]
USER = MYs["MAIN"]["USER"]
PWD = MYs["MAIN"]["PWD"]

# GPIO Setup
#   SERVOGPIO - Pin on the raspberry pi that is controlling the servo
#   WHTOPIC - Topic in the MQTT Broker to monitor for commands. (angle)
#   PULSEFREQUENCY - Frequency of the pulses sent to the servo
#                    The servo expects a pulse every 20ms for between 1ms and 2ms
#                    1ms corresponds to an angle of 0 degrees, while a pulse of 2ms
#                    corresponds to an angle of 180 degrees
#                    - A value of 100(Hz) means that the Pi will send a pulse 100 times per 
#                      second, or once every 10ms.
#   PWM0 - The percentage of time that GPIO pin must be "ON" so that 
#           the motor will turn to angle 0
#           The equation for finding the Correct PWM0, or the pulse modulation 
#                     Required to set the servo to angle 0 is:
#                         DutyCycle = PW/T * 100%
#                         D=1ms/20ms*100 = 5
#           For the motor that you use this may have to be tweaked a bit.
#   TRANGEMIN - For scaling MQTT command to the angle.
#                   This is the temperature represented by servo at angle 0.
#   TRANGEMAX - For scaling MQTT command to the angle.
#                   This is the temperature represented by servo at angle 180.
#
SERVOGPIO = int(MYs["WHCONTROL"]["SERVOGPIO"])
RELAYGPIO = int(MYs["WHCONTROL"]["RELAYGPIO"])
WHTOPIC = MYs["WHCONTROL"]["WHTOPIC"]
PULSEFREQUENCY = float(MYs["WHCONTROL"]["PULSEFREQUENCY"])  #100
TRANGEMIN = float(MYs["WHCONTROL"]["TRANGEMIN"])
TRANGEMAX = float(MYs["WHCONTROL"]["TRANGEMAX"])
PWM0 = float(MYs["WHCONTROL"]["PWM0"])
PWC = float(PWM0*2)
# Set the pinout type to board to use standard board labeling
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
srvo = GPIO.PWM(SERVOGPIO,PULSEFREQUENCY)
chan_list = [SERVOGPIO,RELAYGPIO] 
GPIO.setup(chan_list, GPIO.OUT)
GPIO_ON = GPIO.HIGH
GPIO_OFF = GPIO.LOW

# Pulling the unique MAC SN section address using uuid and getnode() function 
DEVICE_ID = (hex(uuid.getnode())[-6:]).upper()

TOPIC = "homeassistant/sensor/"

NAMED = MYs["TEMP"]["DEVICE_NAME"]
D_ID = DEVICE_ID + '_' + NAMED
STATE = TOPIC + D_ID + '/state'
LWT = TOPIC + D_ID + '/lwt'

NAMEH = MYs["TEMP"]["NAMEH"]
H_ID =  DEVICE_ID + '_' + MYs["TEMP"]["H_ID"]
CONFIGH = TOPIC + H_ID + '/config'

NAMET = MYs["TEMP"]["NAMET"]
T_ID = DEVICE_ID + '_' + MYs["TEMP"]["T_ID"]
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

def on2connect(mqttc, userdata, flags, rc):
    if rc==0:
        print(f"Connecting to MQTT on {HOST} {PORT} with result code {str(rc)}.")
        mqttc.subscribe((WHTOPIC,0))
        # mqttc.subscribe("$SYS/#")
    else:
        print(f"Bad connection Returned code= {str(rc).")

def on2message(mqttc, userdata, msg):
    # The callback for when a PUBLISH message is received from the server.

    Topic = msg.topic
    whSet = float(msg.payload)

    print (f"Message: {str(whSet)} from Topic: {Topic}")

    # Handle Message
    if ( Topic == WHTOPIC and
        isinstance(whSet, float) and
        whSet <= TRANGEMAX and
        whSet >= TRANGEMIN
        ):

        GPIO.output(RELAYGPIO, GPIO_ON)
        time.sleep(2)
        srvo.start(PWC)
        time.sleep(2)
        Angle = whSet
        print (f"Setting Motor to Angle: {Angle}")
        Duty = (Angle / 180) * PWC + PWM0
        # GPIO.output(SERVOGPIO, True)
        print (f"duty: {Duty}")
        srvo.ChangeDutyCycle(Duty)
        time.sleep(2)
        GPIO.output(RELAYGPIO, GPIO_OFF)

def mqttConnect():
    mqttc.on_connect = on2connect
    mqttc.on_message = on2message
    mqttc.connect(HOST, PORT, 60)
    mqttc.loop_start()
    mqttc.publish(LWT, "Online", 1, True)
    mqttc.publish(CONFIGH, json.dumps(payloadHconfig), 1, True)
    mqttc.publish(CONFIGT, json.dumps(payloadTconfig), 1, True)

# Log Message to start
print(f"Logging sensor measurements from {NAMET} & {NAMEH} every {LOOP} seconds.")
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
        print(f"Date Time:   {currentdate}")

        # Publish to MQTT
        try:
            payloadOut = {
                "temperature": tempF,
                "humidity": humidityOut}
            print(f"Updating {STATE} {json.dumps(payloadOut)}'.format")
            (result1,mid) = mqttc.publish(STATE, json.dumps(payloadOut), 1, True)

            print(f"MQTT Update result {result1}")

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

        # Wait before continuing (your variable setting 'LOOP')
        print('Sent values to Home Assistant')
        for i in range(LOOP):
            time.sleep(1)

except KeyboardInterrupt:
    print(' Keyboard Interrupt. Closing MQTT.')
    GPIO.cleanup()
    mqttc.publish(LWT, 'Offline', 1, True)
    time.sleep(1)
    mqttc.loop_stop()
    mqttc.disconnect()
    srvo.stop()
    GPIO.cleanup()
    sys.exit()
