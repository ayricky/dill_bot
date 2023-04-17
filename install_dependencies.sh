#!/bin/sh

apt-get update && \
apt-get install -y libsndfile1 libportaudio2 portaudio19-dev && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*
