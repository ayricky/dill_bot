#!/bin/sh

sudo apt-get update && \
sudo apt-get install -y libsndfile1 libportaudio2 portaudio19-dev ffmpeg && \
sudo apt-get clean
