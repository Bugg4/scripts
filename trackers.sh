#!/bin/sh

mode=$1

if [ -z "$mode" ]; then
    echo "missing mode: use 'all' or 'best'"
    exit 1
fi

curl -s "https://raw.githubusercontent.com/ngosang/trackerslist/refs/heads/master/trackers_${mode}.txt" | wl-copy
echo "${mode} trackers copied to clipboard!"
