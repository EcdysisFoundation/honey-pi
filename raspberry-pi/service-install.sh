#! /bin/bash
set +x
sudo systemctl link ./dht11-py.service
sudo systemctl link ./hx711-py.service
sudo systemctl link ./audio-py.service

sudo systemctl enable dht11-py.service
sudo systemctl enable hx711-py.service
sudo systemctl enable audio-py.service

sudo cp 95-identical-card-names.rules /etc/udev/rules.d/95-identical-card-names.rules 
