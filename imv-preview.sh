#!/usr/bin/env bash

INPUT_IMAGE="$1"

if [ -z "$INPUT_IMAGE" ]; then
    echo "Usage: $0 <image-file>"
    exit 1
fi

# Find imv-wayland process and get its PID
IMV_PID=$(pgrep -u "$USER" -x imv-wayland)

if [ -n "$IMV_PID" ]; then
    # If running, close all images and open the new one
    imv-msg "$IMV_PID" close all && imv-msg "$IMV_PID" open "$INPUT_IMAGE"
else
    # If not running, start imv-wayland with the image and disown
    imv-wayland "$INPUT_IMAGE" &
fi