#!/bin/bash

sudo cp vpn-up /etc/NetworkManager/dispatcher.d/vpn-up
sudo chmod +x /etc/NetworkManager/dispatcher.d/vpn-up

sudo cp wifi-daemon.py /etc/NetworkManager/dispatcher.d/residhotel-login
sudo chmod +x /etc/NetworkManager/dispatcher.d/residhotel-login
