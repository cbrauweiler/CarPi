import xbmc
import xbmcgui
import xbmcaddon
import time
import os
import subprocess
import re
import shlex

# Get global paths
addon = xbmcaddon.Addon(id='plugin.program.wifimanager')
addonpath = addon.getAddonInfo('path').decode("utf-8")
desktop = xbmcgui.Window(10000)
autostart = addon.getSetting('apmodestartup')

def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
	    desktop.setProperty('commandoutput',output.strip())
    rc = process.poll()
    return rc

if autostart == "true":
    time.sleep(20)
    desktop.setProperty('switching','true')
    desktop.setProperty('showifup','false')
    desktop.setProperty('showifdown','false')
    desktop.setProperty('wifiavailable','false')
    realtek = addon.getSetting('realtek')
    if realtek == "true":
        os.system("sudo cp " + str(addonpath) + "/resources/lib/modrealtek/hostapd /usr/sbin/hostapd")
        os.system("sudo cp " + str(addonpath) + "/resources/lib/modrealtek/hostapd_cli /usr/sbin/hostapd_cli")
        os.system("sudo chmod 777 /usr/sbin/hostapd")
        os.system("sudo chmod 777 /usr/sbin/hostapd_cli")
    else:
        os.system("sudo cp " + str(addonpath) + "/resources/lib/raspbian/hostapd /usr/sbin/hostapd")
	os.system("sudo cp " + str(addonpath) + "/resources/lib/raspbian/hostapd_cli /usr/sbin/hostapd_cli")
    	os.system("sudo chmod 777 /usr/sbin/hostapd")
	os.system("sudo chmod 777 /usr/sbin/hostapd_cli")
    desktop.setProperty('commandoutput',"Stopping interface wlan0...")
    run_command("sudo /sbin/ifdown wlan0")
    time.sleep(0.5)
    desktop.setProperty('commandoutput',"Reconfigure interface wlan0 for hostapd...")
    run_command("sudo /sbin/ifconfig wlan0 10.0.0.1 netmask 255.255.255.0 up")
    time.sleep(0.5)
    run_command("sudo /etc/init.d/hostapd start")
    time.sleep(0.5)
    run_command("sudo /etc/init.d/dnsmasq start")
    time.sleep(0.5)
    desktop.setProperty('hostapdactive','true')
    desktop.setProperty('commandoutput',"")
