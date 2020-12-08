#!/bin/bash

echo "Installing pip requirements..."
python3 -m pip install -r requirements.txt  || { echo 'pip install failed' ; exit 1; }
echo "Preparing service..."
sed "s#{INSTALL_DIR}#$(pwd)#" tado-control.service > /tmp/tado-control.service_TMP  || { echo 'sed command failed' ; exit 1; }

echo "Setting up service..."
sudo cp /tmp/tado-control.service_TMP /etc/systemd/system/tado-control.service || { echo 'copy to /tmp failed' ; exit 1; }
sudo systemctl daemon-reload || { echo 'systemctl reload failed' ; exit 1; }
sudo systemctl start tado-control || { echo 'starting the service failed' ; exit 1; }
sudo systemctl enable tado-control || { echo 'enabling the service failed' ; exit 1; }

rm /tmp/tado-control.service_TMP

sudo systemctl status tado-control

echo "Systemd service created successfully."