#!/bin/sh

set -x

systemctl stop waydroid-container.service
waydroid init -f
systemctl start waydroid-container.service
rm -rf /var/lib/waydroid
rm -rf ~/waydroid ~/.share/waydroid ~/.local/share/applications/*aydroid* ~/.local/share/waydroid

set +x
echo Waydroid has been fully reset.
echo Use 'waydroid session start' to start a new session.