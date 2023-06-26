#!/bin/bash
sudo apt update
sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
pip install -U pip
pip install -r requirements.txt
python3 virtual_keyboard.py
