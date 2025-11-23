#!/bin/bash

apt-get -y update || exit 1
apt-get -y install libboost-dev libcgal-dev libgmp-dev libmpfr-dev \
           libvtk9-dev libxi-dev libocct-*-dev occt-misc numdiff || exit 1

