MQTT = {
    'HOST' : 'Broker IP Address Here',
    'PORT' : 'This needs to be a number, usually 1883 as the MQTT port for tcp access',
    'USER' : 'MQTT Username Here',
    'PWD' : 'MQTT User Password Here',
    'TEMP' : 'MQTT temperature topic here, usually node/temperature where node is this device name',
    'HUMI' : 'MQTT humidity topic here, usually node/humidity where node is this device name',
    'LWT' : 'MQTT last will topic here, usually node/lwt where node is this device name',
    'PIN' : 'The GPIO pin used to connect the device',
    'LOOP' : 'This needs to be a number.  Time in seconds for each loop.  Too fast breaks things so I suggest ~ 300 seconds IE 5 minutes.'
    }
