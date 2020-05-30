import xbmc
import xbmcgui
import xbmcaddon
import os
import sys
import socket
import time
import subprocess
from threading import Thread

# Get global paths
addon = xbmcaddon.Addon(id='plugin.program.radioFM')
addonpath = addon.getAddonInfo('path').decode("utf-8")

if str(xbmc.getSkinDir()) == "skin.carpc-xtouch":
    xbmcgui.Window(10000).setProperty('Radio.xtouch','true')
else:
    xbmcgui.Window(10000).setProperty('Radio.xtouch','false')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#control
HOME_BUTTON  = 1101
BACK_BUTTON  = 1102
BUTTON_FOCUS = 1103
TUNE_UP = 1104
TUNE_DOWN = 1105
SEEK_UP = 1106
SEEK_DOWN = 1107
VOLUME_UP = 1108
VOLUME_DOWN = 1109
STORE_BUTTON = 1110
DELETE_BUTTON = 1111
STATIONS_BUTTON = 1112
MUTE_BUTTON = 1113
SETTINGS_BUTTON = 1114
STA1_BUTTON = 1121
STA2_BUTTON = 1122
STA3_BUTTON = 1123
STA4_BUTTON = 1124
STA5_BUTTON = 1125
STA6_BUTTON = 1126
STA7_BUTTON = 1127
STA8_BUTTON = 1128
STA9_BUTTON = 1129
STA10_BUTTON = 1130
ACTION_BACK  = 92

#global used to tell the worker thread the status of the window
windowopen  = True

failsave = str(xbmc.getCondVisibility('System.HasAddon(service.radioFM.watchdog)'))
if failsave == "1":
    xbmcgui.Dialog().ok("$ADDON[plugin.program.radioFM 30029]","$ADDON[plugin.program.radioFM 30030]","$ADDON[plugin.program.radioFM 30031]")
    quit()

def updateWindow():
    global windowopen, mute

    while windowopen and (not xbmc.abortRequested):

        vcheckdb = xbmc.getInfoLabel('Player.Volume')
	vchecksplit = vcheckdb.split(' ')
	vchecktemp = vchecksplit[0]
	vcheck = int(float(vchecktemp)) * -1

	if vcheck <= 56 and vcheck >= 0:
	    xbmc.executebuiltin('Skin.SetBool(MuteVolume,True)')
	    mute = 1

	if vcheck >= 56:
	    xbmc.executebuiltin('Skin.SetBool(MuteVolume,False)')
	    mute = 0

	if str(addon.getSetting('ShowStationLogos')) == "true":
	    radiofreqlogo = xbmcgui.Window(10000).getProperty('Radio.Frequency')
    	    defaultlogopath = addon.getSetting('StationLogosPath')
    	    radiologo = defaultlogopath + radiofreqlogo + ".png"
	    if os.path.isfile(radiologo) == True:
		if xbmcgui.Window(10000).getProperty('Radio.StationLogo') != radiologo:
        	    xbmcgui.Window(10000).setProperty('Radio.Logo','false')
		    time.sleep(0.3)
        	    xbmcgui.Window(10000).setProperty('Radio.StationLogo',radiologo)
        	    xbmcgui.Window(10000).setProperty('Radio.Logo','true')
	    else:
		if xbmcgui.Window(10000).getProperty('Radio.StationLogo') != 'radio_icon_logo.png':
        	    xbmcgui.Window(10000).setProperty('Radio.Logo','false')
		    time.sleep(0.3)
        	    xbmcgui.Window(10000).setProperty('Radio.StationLogo','radio_icon_logo.png')
        	    xbmcgui.Window(10000).setProperty('Radio.Logo','true')
	else:
	    xbmcgui.Window(10000).setProperty('Radio.StationLogo','radio_icon_logo.png')

        time.sleep(1.0)

def CarpcController_SendCommand(command):
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5005

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(command + "\0", (UDP_IP, UDP_PORT))

def Radio_SendCommand(self, command):
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5005
        sock.sendto("radio_" + command + "\0", (UDP_IP, UDP_PORT))

def Init_Values():
	    stationloop = 1
	    while True:
		checkfreq = addon.getSetting('Station' + str(stationloop) + '_Freq')
		checkname = addon.getSetting('Station' + str(stationloop))
		if checkfreq != "" and checkname != "- - -":
		    NewStationString = checkfreq + " - " + checkname
        	    xbmcgui.Window(10000).setProperty('Radio.Station' + str(stationloop),NewStationString)
	        stationloop = stationloop + 1
	        if stationloop > 10:
		    break

	    stationloop = 1
	    while True:
		checkfreq = addon.getSetting('Station' + str(stationloop) + 'b_Freq')
		checkname = addon.getSetting('Station' + str(stationloop) + 'b')
		if checkfreq != "" and checkname != "- - -":
		    NewStationString = checkfreq + " - " + checkname
        	    xbmcgui.Window(10000).setProperty('Radio.Station' + str(stationloop) + 'b',NewStationString)
	        stationloop = stationloop + 1
	        if stationloop > 10:
		    break

	    stationloop = 1
	    while True:
        	station = str(xbmcgui.Window(10000).getProperty('Radio.Station' + str(stationloop)))
		if station == "":
        	    xbmcgui.Window(10000).setProperty('Radio.Station' + str(stationloop),'- - -')
	        stationloop = stationloop + 1
	        if stationloop > 10:
		    break

	    stationloop = 1
	    while True:
        	station = str(xbmcgui.Window(10000).getProperty('Radio.Station' + str(stationloop) + 'b'))
		if station == "":
        	    xbmcgui.Window(10000).setProperty('Radio.Station' + str(stationloop) + 'b','- - -')
	        stationloop = stationloop + 1
	        if stationloop > 10:
		    break

	    bgimage = addon.getSetting('custombackgroundimage')
	    setbgimage = str(addon.getSetting('custombackground'))
	    if setbgimage == "true":
		xbmc.executebuiltin('Skin.SetString(RadioAddonBackgroundImage,' + bgimage + ')')
	    else:
		xbmc.executebuiltin('Skin.SetString(RadioAddonBackgroundImage,radiodefault.jpg)')

	    xbmcgui.Window(10000).setProperty('Radio.ShowRadiotext',str(addon.getSetting('ShowRadiotext')))

Init_Values()

def Tune_Station(self, command):
        storemode = str(xbmc.getCondVisibility('Skin.HasSetting(SaveRadioStation)'))
        delmode = str(xbmc.getCondVisibility('Skin.HasSetting(DeleteRadioStation)'))
        radiolist = str(xbmc.getCondVisibility('Skin.HasSetting(ListRadioStation)'))
        if radiolist == "0" :
	    command = command + 'b'

        if storemode == "1" and delmode == "1": # check if store or delmode active
	    station = str(xbmcgui.Window(10000).getProperty('Radio.' + str(command)))
            requestedFrequency = station.split(' ')
            if str(requestedFrequency[0]) != "-":
		Radio_SendCommand(self, "tune_" + requestedFrequency[0])
    		xbmcgui.Window(10000).setProperty('Radio.Frequency',requestedFrequency[0])
    		xbmcgui.Window(10000).setProperty('Radio.RDS','- - -')
                if str(xbmcgui.Window(10000).getProperty('Radio.Active')) == "false":
	                xbmc.Player().stop()
    	                CarpcController_SendCommand("system_mode_toggle")

def Cleanup_Station(self, command):
        storemode = str(xbmc.getCondVisibility('Skin.HasSetting(SaveRadioStation)'))
        delmode = str(xbmc.getCondVisibility('Skin.HasSetting(DeleteRadioStation)'))
        radiolist = str(xbmc.getCondVisibility('Skin.HasSetting(ListRadioStation)'))
        if radiolist == "0" :
	    command = command + 'b'
	commandfreq = command + '_Freq'

        if storemode == "1" and delmode == "1": # check if store or delmode active
	    station = str(xbmcgui.Window(10000).getProperty('Radio.' + str(command)))
            stationString = station.split('-')
	    stationName = str.strip(stationString[1])
	    stationFrequency = str.strip(stationString[0])

	    if stationName == "":
	    	stationName = "Unknown"
	    if stationFrequency == "":
	    	stationName = "- - -"
    		xbmcgui.Window(10000).setProperty('Radio.' + command,'- - -')
	    else:
		NewStationString = stationFrequency + " - " + stationName
    		xbmcgui.Window(10000).setProperty('Radio.' + command,NewStationString)

	    addon.setSetting(command,stationName)
	    addon.setSetting(commandfreq,stationFrequency)

def Radio_Mute(self):
	global mute
	carpccontrolleraddon = str(xbmc.getCondVisibility('System.HasAddon(service.carpccontroller)'))
	if carpccontrolleraddon == "0":
	    if str(mute) == "1":
		volumedb = xbmc.getInfoLabel('Player.Volume')
        	volumesplit = volumedb.split(' ')
		volumetemp = volumesplit[0]
		volume = int(float(volumetemp)) * -1
		volumeradio = 0
		if volume <= 60 and volume > 56:
		    volumeradio = 0
		if volume <= 56 and volume > 52:
		    volumeradio = 2
		if volume <= 52 and volume > 48:
		    volumeradio = 3
		if volume <= 48 and volume > 44:
		    volumeradio = 4
		if volume <= 44 and volume > 40:
		    volumeradio = 5
		if volume <= 40 and volume > 36:
		    volumeradio = 6
		if volume <= 36 and volume > 32:
		    volumeradio = 7
		if volume <= 32 and volume > 28:
		    volumeradio = 8
		if volume <= 28 and volume > 24:
		    volumeradio = 9
		if volume <= 24 and volume > 20:
		    volumeradio = 10
		if volume <= 20 and volume > 16:
		    volumeradio = 11
		if volume <= 16 and volume > 12:
		    volumeradio = 12
		if volume <= 12 and volume > 8:
		    volumeradio = 13
		if volume <= 8 and volume > 4:
		    volumeradio = 14
		if volume <= 4 and volume > 0:
		    volumeradio = 15
		xbmc.executebuiltin('Skin.SetString(StoredVolume,' + str(volumeradio) + ')')
		storedvolume = volumeradio
		while True:
	            Radio_SendCommand(self,"volume_minus")
		    storedvolume = storedvolume - 1
		    if storedvolume <= 0:
		        break
		mute = 1
	    else:
        	storedvolume = str(xbmc.getInfoLabel('Skin.String("StoredVolume")'))
		counter = int(storedvolume)
		while True:
	            Radio_SendCommand(self,"volume_plus")
		    counter = counter - 1
		    if counter <= 0:
		        break
		mute = 0
	else:
	    getvolume = xbmc.getInfoLabel('Player.Volume')
    	    volumesplit = getvolume.split(' ')
	    volumetemp = volumesplit[0]
	    volumedb = int(float(volumetemp))
	    storevolume = int(1.6667 * (volumedb + 60))

	    if str(addon.getSetting('muted')) == "false":
            	CarpcController_SendCommand('SYSTEM:VOL_0')
		addon.setSetting('muted','true')
		addon.setSetting('storedvolume',str(storevolume))
		xbmc.executebuiltin("SetVolume(0)")
	    else:
		addon.setSetting('muted','false')
		restorevolume = addon.getSetting('storedvolume')
		counter = 0
		while True:
		    counter = counter + 1
            	    CarpcController_SendCommand('SYSTEM:VOL_' + str(counter))
		    xbmc.executebuiltin("SetVolume(" + str(counter) + ")")
		    time.sleep(0.005)
		    if counter >= int(restorevolume):
	    		break

class radiofm(xbmcgui.WindowXMLDialog):

    def onInit(self):
        radiofm.button_home=self.getControl(HOME_BUTTON)
        radiofm.button_back=self.getControl(BACK_BUTTON)
        radiofm.buttonfocus=self.getControl(BUTTON_FOCUS)

    def onAction(self, action):
        global windowopen
        
    def onClick(self, controlID):
    	global windowopen, mute
	carpccontrolleraddon = str(xbmc.getCondVisibility('System.HasAddon(service.carpccontroller)'))

        if controlID == HOME_BUTTON:
            windowopen = False
            self.close()

        if controlID == BACK_BUTTON:
            windowopen = False
            self.close()

        if controlID == TUNE_DOWN:
            if str(xbmcgui.Window(10000).getProperty('Radio.Active')) == "false":
                xbmc.Player().stop()
		if carpccontrolleraddon == "0":
            	    CarpcController_SendCommand("system_mode_toggle")
		else:
            	    CarpcController_SendCommand('SYSTEM:SMODE_1')
		xbmcgui.Window(10000).setProperty('Radio.Active','true')

            Radio_SendCommand(self, "tune_down")
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == TUNE_UP:
            if str(xbmcgui.Window(10000).getProperty('Radio.Active')) == "false":
                xbmc.Player().stop()
		if carpccontrolleraddon == "0":
            	    CarpcController_SendCommand("system_mode_toggle")
		else:
            	    CarpcController_SendCommand('SYSTEM:SMODE_1')
		xbmcgui.Window(10000).setProperty('Radio.Active','true')

            Radio_SendCommand(self, "tune_up")
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == SEEK_DOWN:
            if str(xbmcgui.Window(10000).getProperty('Radio.Active')) == "false":
                xbmc.Player().stop()
		if carpccontrolleraddon == "0":
            	    CarpcController_SendCommand("system_mode_toggle")
		else:
            	    CarpcController_SendCommand('SYSTEM:SMODE_1')
		xbmcgui.Window(10000).setProperty('Radio.Active','true')

            Radio_SendCommand(self, "seek_down")
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == SEEK_UP:
            if str(xbmcgui.Window(10000).getProperty('Radio.Active')) == "false":
                xbmc.Player().stop()
		if carpccontrolleraddon == "0":
            	    CarpcController_SendCommand("system_mode_toggle")
		else:
            	    CarpcController_SendCommand('SYSTEM:SMODE_1')
		xbmcgui.Window(10000).setProperty('Radio.Active','true')

            Radio_SendCommand(self, "seek_up")
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == VOLUME_UP:
            if str(xbmcgui.Window(10000).getProperty('Radio.Active')) == "false":
                xbmc.Player().stop()
		if carpccontrolleraddon == "0":
            	    CarpcController_SendCommand("system_mode_toggle")
		else:
            	    CarpcController_SendCommand('SYSTEM:SMODE_1')

            Radio_SendCommand(self, "volume_plus")
            time.sleep(0.3)
	    self.setFocus(self.buttonfocus)

        if controlID == VOLUME_DOWN:
            if str(xbmcgui.Window(10000).getProperty('Radio.Active')) == "false":
                xbmc.Player().stop()
		if carpccontrolleraddon == "0":
            	    CarpcController_SendCommand("system_mode_toggle")
		else:
            	    CarpcController_SendCommand('SYSTEM:SMODE_1')

            Radio_SendCommand(self, "volume_minus")
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == MUTE_BUTTON:

            if str(xbmcgui.Window(10000).getProperty('Radio.Active')) == "false":
        	xbmc.Player().stop()
		if carpccontrolleraddon == "0":
            	    CarpcController_SendCommand("system_mode_toggle")
		else:
            	    CarpcController_SendCommand('SYSTEM:SMODE_1')
	    Radio_Mute(self)
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STORE_BUTTON:
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == DELETE_BUTTON:
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STATIONS_BUTTON:
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == SETTINGS_BUTTON:
	    addon.openSettings()
	    Init_Values()
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STA1_BUTTON:
	    Tune_Station(self, "Station1")
	    Cleanup_Station(self, "Station1")
	    if carpccontrolleraddon == "1":
        	CarpcController_SendCommand('SYSTEM:SMODE_1')
	    xbmcgui.Window(10000).setProperty('Radio.Active','true')
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STA2_BUTTON:
	    Tune_Station(self, "Station2")
	    Cleanup_Station(self, "Station2")
	    if carpccontrolleraddon == "1":
        	CarpcController_SendCommand('SYSTEM:SMODE_1')
	    xbmcgui.Window(10000).setProperty('Radio.Active','true')
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STA3_BUTTON:
	    Tune_Station(self, "Station3")
	    Cleanup_Station(self, "Station3")
	    if carpccontrolleraddon == "1":
        	CarpcController_SendCommand('SYSTEM:SMODE_1')
	    xbmcgui.Window(10000).setProperty('Radio.Active','true')
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STA4_BUTTON:
	    Tune_Station(self, "Station4")
	    Cleanup_Station(self, "Station4")
	    if carpccontrolleraddon == "1":
        	CarpcController_SendCommand('SYSTEM:SMODE_1')
	    xbmcgui.Window(10000).setProperty('Radio.Active','true')
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STA5_BUTTON:
	    Tune_Station(self, "Station5")
	    Cleanup_Station(self, "Station5")
	    if carpccontrolleraddon == "1":
        	CarpcController_SendCommand('SYSTEM:SMODE_1')
	    xbmcgui.Window(10000).setProperty('Radio.Active','true')
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STA6_BUTTON:
	    Tune_Station(self, "Station6")
	    Cleanup_Station(self, "Station6")
	    if carpccontrolleraddon == "1":
        	CarpcController_SendCommand('SYSTEM:SMODE_1')
	    xbmcgui.Window(10000).setProperty('Radio.Active','true')
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STA7_BUTTON:
	    Tune_Station(self, "Station7")
	    Cleanup_Station(self, "Station7")
	    if carpccontrolleraddon == "1":
        	CarpcController_SendCommand('SYSTEM:SMODE_1')
	    xbmcgui.Window(10000).setProperty('Radio.Active','true')
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STA8_BUTTON:
	    Tune_Station(self, "Station8")
	    Cleanup_Station(self, "Station8")
	    if carpccontrolleraddon == "1":
        	CarpcController_SendCommand('SYSTEM:SMODE_1')
	    xbmcgui.Window(10000).setProperty('Radio.Active','true')
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STA9_BUTTON:
	    Tune_Station(self, "Station9")
	    Cleanup_Station(self, "Station9")
	    if carpccontrolleraddon == "1":
        	CarpcController_SendCommand('SYSTEM:SMODE_1')
	    xbmcgui.Window(10000).setProperty('Radio.Active','true')
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

        if controlID == STA10_BUTTON:
	    Tune_Station(self, "Station10")
	    Cleanup_Station(self, "Station10")
	    if carpccontrolleraddon == "1":
        	CarpcController_SendCommand('SYSTEM:SMODE_1')
	    xbmcgui.Window(10000).setProperty('Radio.Active','true')
            time.sleep(0.3)
            self.setFocus(self.buttonfocus)

    def onFocus(self, controlID):
        pass
    
    def onControl(self, controlID):
        pass
 
fmdialog = radiofm("radiofm.xml", addonpath, 'default', '720')

t1 = Thread( target=updateWindow)
t1.setDaemon( True )
t1.start()

fmdialog.doModal()
del fmdialog



