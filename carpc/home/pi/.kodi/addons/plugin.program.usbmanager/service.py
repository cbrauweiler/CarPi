import xbmc
import xbmcgui
import xbmcaddon
import commands
import time
import subprocess
import os
from threading import Thread
import hashlib
import re
import shlex

# Get global paths
addon = xbmcaddon.Addon(id='plugin.program.usbmanager')
addonpath = addon.getAddonInfo('path').decode("utf-8")
monitor=xbmc.Monitor()
desktop = xbmcgui.Window(10000)
kill = False
addremove = ""
locka = False
lockb = False
TIMER = 0
DTIMER = 0

desktop.setProperty('commandoutput','')
desktop.setProperty('install','false')
desktop.setProperty('installmessage','')
desktop.setProperty('baserequirements','true')
desktop.setProperty('usbautomount','false')
desktop.setProperty('drivechange','true')
desktop.setProperty('showusb1','false')
desktop.setProperty('showusb2','false')
desktop.setProperty('showusb3','false')
desktop.setProperty('showusb4','false')

# check os
if os.path.exists("/etc/os-release"):
    getos = str.strip(subprocess.check_output("sudo cat /etc/os-release | grep ^NAME=", shell=True)).replace('"','').split("=")
    if str(getos[1]) != "Raspbian GNU/Linux":
	xbmcgui.Dialog().ok("OS","$ADDON[plugin.program.usbmanager 30018]")
	quit()
else:
    xbmcgui.Dialog().ok("OS","$ADDON[plugin.program.usbmanager 30018]")
    quit()

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

def mount_drive(command):
	device = desktop.getProperty('usbdevice' + command)
	mounted = desktop.getProperty('usbmounted' + command)
	label = desktop.getProperty('usblabel' + command)
	basefolder = addon.getSetting('basefolder')
	if "Unmounted" in mounted:
	    if label != "" and device != "":
	        os.system("sudo mkdir " + basefolder)
	        os.system("sudo mkdir " + basefolder + "." + label)
	        os.system("sudo chmod 777 " + basefolder + "." + label)
	        os.system("sudo chown pi:pi " + basefolder + "." + label)
	        os.system("sudo mount /dev/" + device + "1 " + basefolder + "." + label)
		mounted = str.strip(subprocess.check_output("df | grep " + device + "1 | tail -n1", shell=True))
		if mounted != "":
		    desktop.setProperty('usbmounted' + str(command),"[COLOR=lightgreen]Mounted[/COLOR]")
		    if addon.getSetting('autolink') == 'true':
			desktop.setProperty('linkmedia','true')
		else:
		    desktop.setProperty('usbmounted' + str(command),"[COLOR=red]Unmounted[/COLOR]")

def check_usb():
    global addremove
    COUNTER = 1
    basefolder = addon.getSetting('basefolder')
    desktop.setProperty('updating','true')
    os.system("sudo chmod 777 " + str(addonpath) + "/resources/lib/listdrives.sh")
    process = subprocess.Popen(shlex.split("sudo " + str(addonpath) + "/resources/lib/listdrives.sh"), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
	    stringsplit = output.strip().split(' ',1)
	    device = stringsplit[0].replace('"','')
	    name = stringsplit[1].replace('"','')
	    label = str.strip(subprocess.check_output("sudo blkid -o value -s LABEL /dev/" + device + "1", shell=True))
	    fstype = str.strip(subprocess.check_output("sudo blkid -o value -s TYPE /dev/" + device + "1", shell=True))
	    fssize = str.strip(subprocess.check_output("lsblk | grep " + device + " | tail -n1 | awk '{print $4}'", shell=True))
	    desktop.setProperty('usb' + str(COUNTER),str(name))
	    desktop.setProperty('usblabel' + str(COUNTER),str(label))
	    desktop.setProperty('usbfstype' + str(COUNTER),str(fstype) + " (" + fssize + ")")
	    mounted = str.strip(subprocess.check_output("df | grep " + device + "1 | tail -n1", shell=True))
	    if mounted != "":
		desktop.setProperty('usbmounted' + str(COUNTER),"[COLOR=lightgreen]Mounted[/COLOR]")
	    else:
		desktop.setProperty('usbmounted' + str(COUNTER),"[COLOR=red]Unmounted[/COLOR]")
	    desktop.setProperty('usbdevice' + str(COUNTER),str(device))
	    fixedmount = str.strip(subprocess.check_output("cat /etc/fstab | grep /dev/" + device + "1 | tail -n1", shell=True))
	    fixedmountlabel = str.strip(subprocess.check_output("cat /etc/fstab | grep " + label + " | tail -n1", shell=True))
	    if fixedmount != "" or fixedmountlabel != "":
	    	desktop.setProperty('showusb' + str(COUNTER),'false')
	    else:
	    	desktop.setProperty('showusb' + str(COUNTER),'true')
	    	COUNTER = COUNTER + 1
    while COUNTER < 4:
        desktop.setProperty('showusb' + str(COUNTER),'false')
        desktop.setProperty('usb' + str(COUNTER),'')
        desktop.setProperty('usbmounted' + str(COUNTER),'')
	desktop.setProperty('usblabel' + str(COUNTER),'')
	desktop.setProperty('usbfstype' + str(COUNTER),'')
        COUNTER = COUNTER + 1
    desktop.setProperty('updating','false')
    
    if addremove == "remove":
	os.system("sudo chmod 777 " + str(addonpath) + "/resources/lib/listmounts.sh")
	process = subprocess.Popen(shlex.split("sudo " + str(addonpath) + "/resources/lib/listmounts.sh"), stdout=subprocess.PIPE)
	while True:
    	    output = process.stdout.readline()
    	    if output == '' and process.poll() is not None:
        	break
    	    if output:
		driveremove = output.split(' ',1)
		if not os.path.exists(driveremove[0]):
		    if driveremove[0] != "" and driveremove[1] != "":
			os.system("sudo umount " + driveremove[0])
			available = str(subprocess.check_output("sudo df | grep " + driveremove[0] + " | tail -n1", shell=True))
			if available == "":
			    os.system("sudo rmdir " + driveremove[1])
			    if addon.getSetting('autolink') == 'true':
    				os.system('find ' + basefolder + ' -type l -exec unlink "{}" ";" &')
        			xbmc.executebuiltin('CleanLibrary(video)');
        			xbmc.executebuiltin('CleanLibrary(music)');
        			xbmc.executebuiltin('CleanLibrary(video)');
        			xbmc.executebuiltin('CleanLibrary(music)');
			else:
		    	    xbmcgui.Dialog().ok("Available","Fehler beim aushaengen")

    if addon.getSetting('automount') == 'true':
	for COUNTER in range (1,4):
	    mount_drive(str(COUNTER))

def check_folders():
    basefolder = addon.getSetting('basefolder')
    moviesfolder = addon.getSetting('moviesfolder')
    musicfolder = addon.getSetting('musicfolder')
    picturesfolder = addon.getSetting('picturesfolder')
    musicvideosfolder = addon.getSetting('musicvideosfolder')
    os.system("sudo mkdir " + basefolder)
    os.system("sudo chmod 777 " + basefolder)
    os.system("sudo mkdir " + basefolder + moviesfolder)
    os.system("sudo chmod 777 " + basefolder + moviesfolder)
    os.system("sudo mkdir " + basefolder + musicfolder)
    os.system("sudo chmod 777 " + basefolder + musicfolder)
    os.system("sudo mkdir " + basefolder + picturesfolder)
    os.system("sudo chmod 777 " + basefolder + picturesfolder)
    os.system("sudo mkdir " + basefolder + musicvideosfolder)
    os.system("sudo chmod 777 " + basefolder + musicvideosfolder)

def link_media():
    basefolder = addon.getSetting('basefolder')
    moviesfolder = addon.getSetting('moviesfolder')
    musicfolder = addon.getSetting('musicfolder')
    picturesfolder = addon.getSetting('picturesfolder')
    musicvideosfolder = addon.getSetting('musicvideosfolder')
    for COUNTER in range (1,4):
	label = desktop.getProperty('usblabel' + str(COUNTER))
	mounted = desktop.getProperty('usbmounted' + str(COUNTER))
	if label != "" and mounted == "[COLOR=lightgreen]Mounted[/COLOR]":
	    if os.path.exists(basefolder + "." + label + "/" + moviesfolder):
		os.system("ln -s " + basefolder + "." + label + "/" + moviesfolder + "/* " + basefolder + moviesfolder)
	    if os.path.exists(basefolder + "." + label + "/" + musicfolder):
		os.system("ln -s " + basefolder + "." + label + "/" + musicfolder + "/* " + basefolder + musicfolder)
	    if os.path.exists(basefolder + "." + label + "/" + picturesfolder):
		os.system("ln -s " + basefolder + "." + label + "/" + picturesfolder + "/* " + basefolder + picturesfolder)
	    if os.path.exists(basefolder + "." + label + "/" + musicvideosfolder):
		os.system("ln -s " + basefolder + "." + label + "/" + musicvideosfolder + "/* " + basefolder + musicvideosfolder)
    xbmc.executebuiltin('UpdateLibrary(video)');
    xbmc.executebuiltin('UpdateLibrary(music)');

connected = int(str.strip(subprocess.check_output("ls -l /dev/sd* | wc -l", shell=True)))

while not monitor.abortRequested():

    if TIMER > 30 and addon.getSetting('startupcheck') == 'true':
        newconnected  = int(str.strip(subprocess.check_output("ls -l /dev/sd* | wc -l", shell=True)))
        if newconnected != connected:
    	    if newconnected > connected:
		connected = newconnected
		addremove = "add"
		check_usb()
		addremove = ""
	    else:
		connected = newconnected
		addremove = "remove"
		check_usb()
		addremove = ""
        TIMER = 0

	if desktop.getProperty('linkmedia') == 'true':
	    desktop.setProperty('linkmedia','false')
	    check_folders()
	    link_media()

    if DTIMER > 6 and addon.getSetting('startupcheck') == 'true':
	if desktop.getProperty('drivechange') == 'true':
	    check_usb()
	    if addon.getSetting('autolink') == 'true':
		check_folders()
		link_media()
	    desktop.setProperty('drivechange','false')
	DTIMER = 0

    TIMER = TIMER + 1
    DTIMER = DTIMER + 1
    time.sleep(0.3)
quit()