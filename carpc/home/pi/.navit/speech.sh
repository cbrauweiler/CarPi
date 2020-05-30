#!/bin/bash

# Bugfixed by hawkeyexp
#echo '$1' > /home/pi/out
# f4 - female voice 4
# -s speed
# -g delay between words
sudo aplay -r 44100 /home/pi/.navit/notification3.wav & sleep 0.7 && sudo espeak -ven+f4 -s150 -a 150 -p 50 "$1" --stdout | aplay
