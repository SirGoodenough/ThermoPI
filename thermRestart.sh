#!/bin/sh

ps auxw | grep furnace.py | grep -v grep > /dev/null

if [ $? != 0 ]
then
        systemctl restart ThermoPI.service > /dev/null
fi

