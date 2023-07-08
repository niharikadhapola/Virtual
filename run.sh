#!/bin/bash


# Update package lists
apt update

# Install GStreamer development libraries and plugins
apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
pip install pygobject

pip install -U pip
pip install -r requirements.txt

