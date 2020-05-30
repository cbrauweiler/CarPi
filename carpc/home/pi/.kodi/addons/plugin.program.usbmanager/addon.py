import xbmc
import xbmcgui
import xbmcaddon
import commands
import time
import subprocess
import os
#from threading import Thread
#import hashlib
#import re
import shlex

# Get global paths
addon = xbmcaddon.Addon(id='plugin.program.usbmanager')
addonpath = addon.getAddonInfo('path').decode("utf-8")
desktop = xbmcgui.Window(10000)

#control
HOME_BUTTON = 1201
BACK_BUTTON = 1202
BUTTON_FOCUS = 1203
SETTINGS_BUTTON = 1204
ACTION_BACK = 92
BUTTON_1 = 1205
BUTTON_2 = 1206
BUTTON_3 = 1207
BUTTON_4 = 1208
BUTTON_LINK = 1209

desktop.setProperty('commandoutput','')
desktop.setProperty('install','false')
desktop.setProperty('installmessage','')
desktop.setProperty('baserequirements','true')
if addon.getSetting('automount') == 'true':
    desktop.setProperty('automount','true')
else:
    desktop.setProperty('automount','false')

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

def pkg_exists(cmd):
    check = str.strip(subprocess.check_output("dpkg -l | awk '$2==\"" + cmd + "\" { print $3 }'", shell=True))
    if check != "":
	return "ok"
    else:
	return "missing"

def check_base():
    if pkg_exists("ntfs-3g") != "ok" or pkg_exists("exfat-fuse") != "ok" or pkg_exists("exfat-utils") != "ok" or pkg_exists("hfsplus") != "ok" or pkg_exists("hfsprogs") != "ok" or pkg_exists("hfsutils") != "ok" or pkg_exists("gvfs") == "ok" or pkg_exists("usbmount") == "ok":
	ask = xbmcgui.Dialog().yesno("$ADDON[plugin.program.usbmanager 30008]","$ADDON[plugin.program.usbmanager 30009]")
	if ask == 1:
	    inet = str.strip(subprocess.check_output('ping -c2 www.google.de >/dev/null 2>&1 || echo "fail"', shell=True))
	    desktop.setProperty('install','true')
	    if inet != "fail":
		time.sleep(1)
		if pkg_exists("ntfs-3g") != "ok":
		    desktop.setProperty('installmessage',addon.getLocalizedString(30040))
		    run_command("sudo apt-get install -f -y ntfs-3g")
		    if pkg_exists("ntfs-3g") != "ok":
			desktop.setProperty('baserequirements','false')
		if pkg_exists("exfat-fuse") != "ok":
		    desktop.setProperty('installmessage',addon.getLocalizedString(30041))
		    run_command("sudo apt-get install -f -y exfat-fuse")
		    if pkg_exists("exfat-fuse") != "ok":
			desktop.setProperty('baserequirements','false')
		if pkg_exists("exfat-utils") != "ok":
		    desktop.setProperty('installmessage',addon.getLocalizedString(30039))
		    run_command("sudo apt-get install -f -y exfat-utils")
		    if pkg_exists("exfat-utils") != "ok":
			desktop.setProperty('baserequirements','false')
		if pkg_exists("hfsplus") != "ok":
		    desktop.setProperty('installmessage',addon.getLocalizedString(30054))
		    run_command("sudo apt-get install -f -y hfsplus")
		    if pkg_exists("hfsplus") != "ok":
			desktop.setProperty('baserequirements','false')
		if pkg_exists("hfsprogs") != "ok":
		    desktop.setProperty('installmessage',addon.getLocalizedString(30055))
		    run_command("sudo apt-get install -f -y hfsprogs")
		    if pkg_exists("hfsprogs") != "ok":
			desktop.setProperty('baserequirements','false')
		if pkg_exists("hfsutils") != "ok":
		    desktop.setProperty('installmessage',addon.getLocalizedString(30056))
		    run_command("sudo apt-get install -f -y hfsutils")
		    if pkg_exists("hfsutils") != "ok":
			desktop.setProperty('baserequirements','false')
		if pkg_exists("gvfs") == "ok":
		    desktop.setProperty('installmessage',addon.getLocalizedString(30057))
		    run_command("sudo apt-get remove --purge -f -y gvfs gvfs-*")
		    if pkg_exists("gvfs") == "ok":
			desktop.setProperty('baserequirements','false')
		if pkg_exists("usbmount") == "ok":
		    desktop.setProperty('installmessage',addon.getLocalizedString(30058))
		    run_command("sudo apt-get remove --purge -f -y usbmount")
		    if pkg_exists("usbmount") == "ok":
			desktop.setProperty('baserequirements','false')

		if pkg_exists("ntfs-3g") == "ok" and pkg_exists("exfat-fuse") == "ok" and pkg_exists("exfat-utils") == "ok" and pkg_exists("hfsplus") == "ok" and pkg_exists("hfsprogs") == "ok" and pkg_exists("hfsutils") == "ok" and pkg_exists("gvfs") != "ok" and pkg_exists("usbmount") != "ok":
		    desktop.setProperty('baserequirements','true')
		    desktop.setProperty('install','false')
		    desktop.setProperty('installmessage',"")
    		    addon.setSetting('startupcheck','true')
	    else:
		desktop.setProperty('installmessage','[COLOR red]' + addon.getLocalizedString(30007) + "[CR]" + addon.getLocalizedString(30026) + '[/COLOR]')
		time.sleep(5)
		desktop.setProperty('baserequirements','false')
		desktop.setProperty('install','false')
		desktop.setProperty('installmessage',"")
	else:
	    desktop.setProperty('baserequirements','false')
	    desktop.setProperty('install','false')
	
    else:
        desktop.setProperty('baserequirements','true')
        addon.setSetting('startupcheck','true')

def mount_drive(command):
	device = desktop.getProperty('usbdevice' + command)
	mounted = desktop.getProperty('usbmounted' + command)
	label = desktop.getProperty('usblabel' + command)
	basefolder = addon.getSetting('basefolder')
	if "Unmounted" in mounted and addon.getSetting('automount') != 'true':
	    # Mount drive
	    ask = xbmcgui.Dialog().yesno("$ADDON[plugin.program.usbmanager 30001]","$ADDON[plugin.program.usbmanager 30003]")
	    if ask == 1:
		if label != "" and device != "":
		    os.system("sudo mkdir " + basefolder)
		    os.system("sudo mkdir " + basefolder + "/." + label)
		    os.system("sudo chmod 777 " + basefolder + "/." + label)
		    os.system("sudo chown pi:pi " + basefolder + "/." + label)
		    os.system("sudo mount /dev/" + device + "1 " + basefolder + "/." + label)
		    desktop.setProperty('drivechange','true')
		else:
		    xbmcgui.Dialog().ok("$ADDON[plugin.program.usbmanager 30005]","$ADDON[plugin.program.usbmanager 30006]")
    		    
	else:
	    # Unmount drive
	    ask = xbmcgui.Dialog().yesno("$ADDON[plugin.program.usbmanager 30002]","$ADDON[plugin.program.usbmanager 30004]")
	    if ask == 1:
		os.system("sudo umount /dev/" + device + "1")
		os.system("sudo rmdir " + basefolder + "/." + label)
		desktop.setProperty('drivechange','true')
		if addon.getSetting('autolink') == 'true':
		    os.system('find ' + basefolder + ' -type l -exec unlink "{}" ";" &')
		    xbmc.executebuiltin('CleanLibrary(video)');
		    xbmc.executebuiltin('CleanLibrary(music)');
	
class usbmanager(xbmcgui.WindowXMLDialog):
    def onInit(self):
        usbmanager.button_home=self.getControl(HOME_BUTTON)
        usbmanager.button_back=self.getControl(BACK_BUTTON)
        usbmanager.buttonfocus=self.getControl(BUTTON_FOCUS)
        usbmanager.button_1=self.getControl(BUTTON_1)
        usbmanager.button_2=self.getControl(BUTTON_2)
        usbmanager.button_3=self.getControl(BUTTON_3)
        usbmanager.button_4=self.getControl(BUTTON_4)
        usbmanager.button_settings=self.getControl(SETTINGS_BUTTON)
	check_base()

    def onAction(self, action):
    	pass
        
    def onClick(self, controlID):

        if controlID == HOME_BUTTON:
	    self.setFocus(self.buttonfocus)
	    time.sleep(0.3)
            self.close()

        if controlID == BACK_BUTTON:
	    self.setFocus(self.buttonfocus)
	    time.sleep(0.3)
            self.close()

        if controlID == SETTINGS_BUTTON:
	    self.setFocus(self.buttonfocus)
	    addon.openSettings()
	    if addon.getSetting('automount') == 'true':
		desktop.setProperty('automount','true')
		#desktop.setProperty('drivechange','true')
	    else:
		desktop.setProperty('automount','false')
	    desktop.setProperty('drivechange','true')
	    self.setFocus(self.buttonfocus)

        if controlID == BUTTON_1:
	    self.setFocus(self.buttonfocus)
	    if addon.getSetting('automount') != 'true':
		mount_drive('1')
	    time.sleep(0.3)

        if controlID == BUTTON_2:
	    self.setFocus(self.buttonfocus)
	    if addon.getSetting('automount') != 'true':
		mount_drive('2')
	    time.sleep(0.3)

        if controlID == BUTTON_3:
	    self.setFocus(self.buttonfocus)
	    if addon.getSetting('automount') != 'true':
		mount_drive('3')
	    time.sleep(0.3)

        if controlID == BUTTON_4:
	    self.setFocus(self.buttonfocus)
	    if addon.getSetting('automount') != 'true':
		mount_drive('4')
	    time.sleep(0.3)

    def onFocus(self, controlID):
        pass
    
    def onControl(self, controlID):
        pass

usbmanagerdialog = usbmanager("Custom_USBManager.xml", addonpath, 'default', '720')
usbmanagerdialog.doModal()
del usbmanagerdialog
