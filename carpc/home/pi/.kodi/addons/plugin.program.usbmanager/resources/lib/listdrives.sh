#!/bin/bash

export USBKEYS=($(
    grep -Hv ^0$ /sys/block/*/removable |
    sed s/removable:.*$/device\\/uevent/ |
    xargs grep -H ^DRIVER=sd |
    sed s/device.uevent.*$/size/ |
    xargs grep -Hv ^0$ |
    cut -d / -f 4
))
for dev in ${USBKEYS[@]} ;do
    echo $dev \"$(
        sed -e s/\ *$//g </sys/block/$dev/device/model
        )\" ;
  done
