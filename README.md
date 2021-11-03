# ThermoPI
Use a Raspberry PI connected to one or more temperature sensors to send the results to a MQTT server.

## USAGE:
Install the program into opt/ThermoPI or any suitable location. (Some people like /usr/local/bin instead of /opt)

You will need to rename the file ***MYsecretsSample.yml*** to ***MYsecrets.yml***.
Edit the contents of the new ***MYsecrets.yml*** to match your MQTT installation and requirements.

To start the program looping, you can write a short script to call like the example give in gpio4.sh.  This script needs to be executable.

To run the program at boot in order to get constant readings, 
    see the Example-rc.local file and do something similar.
    There is also ThermoPI.service to run this as a service with load-service.sh there to set it up as a service. (preferred)

The Python program itself is well documented.

Program requirements (as written):  (feel free to fork it and convert to Python 3.8 or updating the DHT Libraries to CircuitPython DHT Libraries and dropping me a merge request...)
+ Python 2.7 
+ PyYAML        (https://pypi.org/project/PyYAML/)
+ Adafruit_DHT  (https://github.com/adafruit/Adafruit_Python_DHT)
+ paho-mqtt     (https://pypi.org/project/paho-mqtt/)

If you have any questions, comments or additions be sure to add an issue and bring them up on my Discord Server: 

## Contact Links:
* [What are we Fixing Today Homepage](https://www.WhatAreWeFixing.Today/)
* [YouYube Channel Link](https://bit.ly/WhatAreWeFixingTodaysYT)
* [What are we Fixing Today Facebook page](https://bit.ly/WhatAreWeFixingTodayFB)
* [What are we Fixing Today Twitter](https://bit.ly/WhatAreWeFixingTodayTW)
* [Discord WhatAreWeFixingToday](https://discord.gg/Uhmhu3B)

### Please help support the channel:

* [Patreon Membership](https://www.patreon.com/WhatAreWeFixingToday)

* [Buy me Coffee](https://www.buymeacoffee.com/SirGoodenough)
* [PayPal one-off donation link](https://www.paypal.me/SirGoodenough)
* [Cash App \$CASHTAG](https://cash.me/$SirGoodenough)
* [Venmo cash link](https://venmo.com/SirGoodenough)


## Disclaimer

:warning: **DANGER OF ELECTROCUTION** :warning:

If your device connects to mains electricity (AC power) there is danger of electrocution if not installed properly. If you don't know how to install it, please call an electrician (***Beware:*** certain countries prohibit installation without a licensed electrician present). Remember: _**SAFETY FIRST**_. It is not worth the risk to yourself, your family and your home if you don't know exactly what you are doing. Never tinker or try to flash a device using the serial programming interface while it is connected to MAINS ELECTRICITY (AC power).

We don't take any responsibility nor liability for using this software nor for the installation or any tips, advice, videos, etc. given by any member of this site or any related site.
