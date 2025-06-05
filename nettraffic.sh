#!/bin/bash

bmon -p enp0s31f6 -o ascii -r 0.1 -R 0.1 | awk '/enp0s31f6/ {print "RX: "$2"\nTX: "$4"\n"}'
