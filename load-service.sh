#!/bin/sh

echo "Stopping ThermoPI"
sudo systemctl stop ThermoPI.service  

echo "Copy file over"
sudo cp /opt/ThermoPI/ThermoPI.service /lib/systemd/system/ThermoPI.service

echo "Change permissions on new file"
sudo chmod 644 /lib/systemd/system/ThermoPI.service

echo "Reload the systemd daemon"
sudo systemctl daemon-reload

echo "Enable the new service"
sudo systemctl enable ThermoPI.service

echo "Start the new service"
sudo systemctl start ThermoPI.service  

echo "Check that the new service is running"
# Delay to give the pi a chance to think
sleep 7

sudo systemctl status ThermoPI.service
