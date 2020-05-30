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
addon = xbmcaddon.Addon(id='plugin.program.wifimanager')
addonpath = addon.getAddonInfo('path').decode("utf-8")
monitor=xbmc.Monitor()
desktop = xbmcgui.Window(10000)
hotspoterequirements = 0
kill = False
pause = False
updated = False
execute = False
timer = 28
baserequirementsmissing = False

#control
HOME_BUTTON  = 1201
BACK_BUTTON  = 1202
BUTTON_FOCUS = 1203
SETTINGS_BUTTON  = 1204
ACTION_BACK  = 92
NETWORK1_BUTTON  = 1205
NETWORK2_BUTTON  = 1206
NETWORK3_BUTTON  = 1207
NETWORK4_BUTTON  = 1208
WIFI_BUTTON  = 1209
APMODE_BUTTON  = 1210
HOSTAPD_BUTTON  = 1211
DNSMASQ_BUTTON  = 1212
DISCONNECT_BUTTON  = 1213
CONNECT_BUTTON  = 1214

desktop.setProperty('apmodepossible','false')
desktop.setProperty('wifiavailable','false')
desktop.setProperty('hostapdactive','false')
desktop.setProperty('switching','false')
desktop.setProperty('install','true')
desktop.setProperty('baserequirements','true')
desktop.setProperty('startup','true')
desktop.setProperty('showifup','false')
desktop.setProperty('showifdown','true')
desktop.setProperty('clientoffline','false')
desktop.setProperty('commandoutput',"")

# check os
if os.path.exists("/etc/os-release"):
    getos = str.strip(subprocess.check_output("sudo cat /etc/os-release | grep ^NAME=", shell=True)).replace('"','').split("=")
    if str(getos[1]) != "Raspbian GNU/Linux":
	xbmcgui.Dialog().ok("OS","$ADDON[plugin.program.wifimanager 30018]")
	quit()
else:
    xbmcgui.Dialog().ok("OS","$ADDON[plugin.program.wifimanager 30018]")
    quit()

def check_if(interface):
    #getstate = str.strip(subprocess.check_output("sudo cat /sys/class/net/" + str(interface) + "/operstate", shell=True))
    getstate = str.strip(subprocess.check_output("ps -ax | grep wpa_supplicant | grep -v grep | tail -n1", shell=True))
    if getstate != "":
	getstate = "up"
    else:
	getstate = "down"
	#state = str(getstate)
    return getstate

def getrevision():
    revision = "unknown"
    with open('/proc/cmdline', 'r') as f:
	line = f.readline()
	m = re.search('bcm2709.boardrev=(0x[0123456789abcdef]*) ', line)
	if str(m) != "None":
	    revision = m.group(1)
	    if revision == "0x2a02082" or revision == "0x2a22082" or revision == "0xa02082" or revision == "0xa22082":
		revision = "RPi3"
		if addon.getSetting('realtek') == "true":
		    xbmcgui.Dialog().ok("$ADDON[plugin.program.wifimanager 30033]","$ADDON[plugin.program.wifimanager 30043]","$ADDON[plugin.program.wifimanager 30044]")
		    addon.setSetting('realtek','false')
    return revision

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

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

def check_md5(filePath):
    if os.path.exists(filePath):
	with open(filePath, 'rb') as fh:
    	    m = hashlib.md5()
    	    while True:
        	data = fh.read(8192)
        	if not data:
            	    break
        	m.update(data)
    	    return m.hexdigest()
    else:
	return "12345"

def check_base():
    global kill, pause, networklist, updated
    pause = True
    if cmd_exists("iwlist") == 0 or cmd_exists("wpa_cli") == 0:
	ask = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30008]","$ADDON[plugin.program.wifimanager 30009]")
	if ask == 1:
	    inet = str.strip(subprocess.check_output('ping -c2 www.google.de >/dev/null 2>&1 || echo "fail"', shell=True))
	    desktop.setProperty('install','true')
	    if inet != "fail":
		time.sleep(1)
		if updated == False:
		    desktop.setProperty('installmessage','[COLOR lightgreen]' + addon.getLocalizedString(30025) + '[/COLOR]')
		    time.sleep(1)
		    desktop.setProperty('installmessage',addon.getLocalizedString(30015))
		    run_command("sudo apt-get update")
		    updated = True
		desktop.setProperty('installmessage','[COLOR lightgreen]' + addon.getLocalizedString(30025) + '[/COLOR]')
		time.sleep(1)
		if pkg_exists("wpasupplicant") != "ok":
		    desktop.setProperty('installmessage',addon.getLocalizedString(30040))
		    run_command("sudo apt-get install -f -y wpasupplicant")
		    if pkg_exists("wpasupplicant") != "ok":
			desktop.setProperty('baserequirements','false')
		if pkg_exists("wireless-tools") != "ok":
		    desktop.setProperty('installmessage',addon.getLocalizedString(30041))
		    run_command("sudo apt-get install -f -y wireless-tools")
		    if pkg_exists("wireless-tools") != "ok":
			desktop.setProperty('baserequirements','false')

	    else:
		desktop.setProperty('installmessage','[COLOR red]' + addon.getLocalizedString(30026) + '[/COLOR]')
		kill = True
		time.sleep(5)
		desktop.setProperty('baserequirements','false')
		desktop.setProperty('apmodepossible','false')
		desktop.setProperty('wifiavailable','false')
		desktop.setProperty('install','false')
		desktop.setProperty('installmessage',"")
	else:
	    kill = True
	    desktop.setProperty('baserequirements','false')
	    desktop.setProperty('apmodepossible','false')
	    desktop.setProperty('wifiavailable','false')
	    desktop.setProperty('install','false')
	    desktop.setProperty('installmessage',"")

def checkInstall():
    global kill, pause, networklist, updated
    check_base()
    desktop.setProperty('hotspotssid',"")    
    apmodesetting = addon.getSetting('apmode')
    realtek = addon.getSetting('realtek')
    apmodessid = addon.getSetting('ssid')
    apmodepassword = addon.getSetting('password')
    os.system("sudo cp " + str(addonpath) + "/resources/lib/hostapd.master " + str(addonpath) + "/resources/lib/hostapd.conf")
    if realtek == "true":
	os.system("echo 'driver=rtl871xdrv' >> " + str(addonpath) + "/resources/lib/hostapd.conf")
    else:
	os.system("sed -i 's/driver=rtl871xdrv//g'" + str(addonpath) + "/resources/lib/hostapd.conf")
    os.system("sed -i 's/ssid=CARPI/ssid=" + apmodessid + "/g' " + str(addonpath) + "/resources/lib/hostapd.conf")
    os.system("sed -i 's/wpa_passphrase=1234567890/wpa_passphrase=" + apmodepassword + "/g' " + str(addonpath) + "/resources/lib/hostapd.conf")
    desktop.setProperty('hotspotssid',str(apmodessid))

    if apmodesetting == "true":
	hostapdavailable = pkg_exists("hostapd")
	dnsmasqavailable = pkg_exists("dnsmasq")
	if check_md5('/etc/hostapd/hostapd.conf') == check_md5(str(addonpath) + "/resources/lib/hostapd.conf"):
	    md5hostapdcheck = "ok"
	else:
	    md5hostapdcheck = "fail"

	if check_md5('/etc/default/hostapd') == check_md5(str(addonpath) + "/resources/lib/hostapd"):
	    md5hostapddefaultcheck = "ok"
	else:
	    md5hostapddefaultcheck = "fail"

	if check_md5('/etc/dnsmasq.conf') == check_md5(str(addonpath) + "/resources/lib/dnsmasq.conf"):
	    md5dnsmasqcheck = "ok"
	else:
	    md5dnsmasqcheck = "fail"

	if hostapdavailable == "missing" or dnsmasqavailable == "missing"  or md5hostapdcheck == "fail" or md5hostapddefaultcheck == "fail" or md5dnsmasqcheck == "fail":
	    pause = True
	    if hostapdavailable == "ok" and dnsmasqavailable == "ok":
		ask = 1
	    else:
		ask = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30019]","$ADDON[plugin.program.wifimanager 30020]")
	else:
	    ask = 0

	if ask == 1:
	    inet = str.strip(subprocess.check_output('ping -c2 www.google.de >/dev/null 2>&1 || echo "fail"', shell=True))
	    desktop.setProperty('install','true')
	    if inet != "fail":
		time.sleep(1)
		if hostapdavailable != "ok":
		    if updated == False:
			desktop.setProperty('installmessage','[COLOR lightgreen]' + addon.getLocalizedString(30025) + '[/COLOR]')
			time.sleep(1)
			desktop.setProperty('installmessage',addon.getLocalizedString(30015))
			run_command("sudo apt-get update")
			updated = True
		    desktop.setProperty('installmessage','[COLOR lightgreen]' + addon.getLocalizedString(30025) + '[/COLOR]')
		    time.sleep(1)
		    desktop.setProperty('installmessage',addon.getLocalizedString(30013))
		    run_command("sudo apt-get install --force-yes -q -f -y hostapd -o Dpkg::Options::=\"--force-confdef\" -o Dpkg::Options::=\"--force-confold\"")
		    if pkg_exists("hostapd") == "ok":
    			os.system("sudo update-rc.d hostapd disable")
    			os.system("sudo /etc/init.d/hostapd stop")
			os.system("sudo cp " + str(addonpath) + "/resources/lib/hostapd.conf" + " /etc/hostapd/hostapd.conf")
			hostapdavailable = pkg_exists("hostapd")
		    else:
			xbmcgui.Dialog().ok("$ADDON[plugin.program.wifimanager 30007]","$ADDON[plugin.program.wifimanager 30011]")

		if dnsmasqavailable != "ok":
		    if updated == False:
			desktop.setProperty('installmessage','[COLOR lightgreen]' + addon.getLocalizedString(30025) + '[/COLOR]')
			time.sleep(1)
			desktop.setProperty('installmessage',addon.getLocalizedString(30015))
			run_command("sudo apt-get update")
			updated = True
		    desktop.setProperty('installmessage','[COLOR lightgreen]' + addon.getLocalizedString(30025) + '[/COLOR]')
		    time.sleep(1)
		    desktop.setProperty('installmessage',addon.getLocalizedString(30014))
		    run_command("sudo apt-get install --force-yes -q -f -y dnsmasq -o Dpkg::Options::=\"--force-confdef\" -o Dpkg::Options::=\"--force-confold\"")
		    if pkg_exists("dnsmasq") == "ok":
			os.system("sudo update-rc.d dnsmasq disable")
    			os.system("sudo /etc/init.d/dnsmasq stop")
			os.system("sudo cp " + str(addonpath) + "/resources/lib/dnsmasq.conf" + " /etc/dnsmasq.conf")
			dnsmasqavailable = pkg_exists("dnsmasq")
		    else:
			xbmcgui.Dialog().ok("$ADDON[plugin.program.wifimanager 30007]","$ADDON[plugin.program.wifimanager 30012]")
	    else:
		desktop.setProperty('installmessage','[COLOR red]' + addon.getLocalizedString(30026) + '[/COLOR]')
	    time.sleep(5)

	    if hostapdavailable == "ok" and md5hostapdcheck != "ok":
		desktop.setProperty('installmessage',addon.getLocalizedString(30027))
		time.sleep(1)
		os.system("sudo cp " + str(addonpath) + "/resources/lib/hostapd.conf" + " /etc/hostapd/hostapd.conf")
		if check_md5('/etc/hostapd/hostapd.conf') == check_md5(str(addonpath) + "/resources/lib/hostapd.conf"):
		    md5hostapdcheck = "ok"
		else:
		    md5hostapdcheck = "fail"
	    else:
		if check_md5('/etc/hostapd/hostapd.conf') == check_md5(str(addonpath) + "/resources/lib/hostapd.conf"):
		    md5hostapdcheck = "ok"
		else:
		    md5hostapdcheck = "fail"

	    if hostapdavailable == "ok" and md5hostapddefaultcheck != "ok":
		desktop.setProperty('installmessage',addon.getLocalizedString(30027))
		time.sleep(1)
		os.system("sudo cp " + str(addonpath) + "/resources/lib/hostapd" + " /etc/default/hostapd")
		if check_md5('/etc/default/hostapd') == check_md5(str(addonpath) + "/resources/lib/hostapd"):
		    md5hostapddefaultcheck = "ok"
		else:
		    md5hostapddefaultcheck = "fail"
	    else:
		if check_md5('/etc/default/hostapd') == check_md5(str(addonpath) + "/resources/lib/hostapd"):
		    md5hostapddefaultcheck = "ok"
		else:
		    md5hostapddefaultcheck = "fail"

	    if dnsmasqavailable == "ok" and md5dnsmasqcheck != "ok":
		desktop.setProperty('installmessage',addon.getLocalizedString(30028))
		time.sleep(1)
		os.system("sudo cp " + str(addonpath) + "/resources/lib/dnsmasq.conf" + " /etc/dnsmasq.conf")
		if check_md5('/etc/dnsmasq.conf') == check_md5(str(addonpath) + "/resources/lib/dnsmasq.conf"):
		    md5dnsmasqcheck = "ok"
		else:
		    md5dnsmasqcheck = "fail"
	    else:
		if check_md5('/etc/dnsmasq.conf') == check_md5(str(addonpath) + "/resources/lib/dnsmasq.conf"):
		    md5dnsmasqcheck = "ok"
		else:
		    md5dnsmasqcheck = "fail"

    if apmodesetting == "true" and hostapdavailable == "ok" and dnsmasqavailable == "ok" and md5hostapdcheck == "ok" and md5hostapddefaultcheck == "ok" and md5dnsmasqcheck == "ok":
	desktop.setProperty('apmodepossible','true')
	desktop.setProperty('install','false')
	desktop.setProperty('installmessage',"")
	pause = False
    else:
	desktop.setProperty('apmodepossible','false')
	desktop.setProperty('install','false')
	desktop.setProperty('installmessage',"")
	pause = False

def scanNetworks():
    global networklist
    checkifupdown = check_if("wlan0")
    checkip = str.strip(subprocess.check_output("sudo hostname -I | cut -d' ' -f1", shell=True))
    desktop.setProperty('ipaddress',str(checkip))
    checkif = subprocess.Popen(["sudo ifconfig | grep wlan0 | cut -d' ' -f1 | tail -n1"], shell=True, stdout=subprocess.PIPE).stdout
    checkifresult = checkif.read().splitlines()
    checkhostapd = subprocess.Popen(["sudo ps -ax | grep hostapd | grep -v grep | cut -d? -f1"], shell=True, stdout=subprocess.PIPE).stdout
    checkdnsmasq = subprocess.Popen(["sudo ps -ax | grep dnsmasq | grep -v grep | cut -d? -f1"], shell=True, stdout=subprocess.PIPE).stdout
    checkhostapdstate = checkhostapd.read().splitlines()
    checkdnsmasqstate = checkdnsmasq.read().splitlines()
    if len(checkhostapdstate) > 0:
	desktop.setProperty('hostapdicon',"wifiman_icon_current.png")
    else:
	desktop.setProperty('hostapdicon',"wifiman_icon_disabled.png")

    if len(checkdnsmasqstate) > 0:
	desktop.setProperty('dnsmasqicon',"wifiman_icon_current.png")
    else:
	desktop.setProperty('dnsmasqicon',"wifiman_icon_disabled.png")

    if len(checkhostapdstate) > 0 and len(checkdnsmasqstate) > 0:
    	desktop.setProperty('storednet1',str(checkhostapdstate[0]).replace(" ",""))

    if str(checkifresult[0]) == "wlan0" and len(checkhostapdstate) == 0 and len(checkdnsmasqstate) == 0:
	desktop.setProperty('wifiavailable','true')
	desktop.setProperty('hostapdactive','false')
	desktop.setProperty('textcolor1',"white")
	desktop.setProperty('textcolor2',"white")
	desktop.setProperty('textcolor3',"white")
	desktop.setProperty('textcolor4',"white")
	desktop.setProperty('textcolor5',"white")
	desktop.setProperty('textcolor6',"white")
	desktop.setProperty('textcolor7',"white")
	desktop.setProperty('textcolor8',"white")

	desktop.setProperty('scanlist1',xbmc.getInfoLabel('$ADDON[plugin.program.wifimanager 30000]'))
	desktop.setProperty('scanlist2',"")
	desktop.setProperty('scanlist3',"")
	desktop.setProperty('scanlist4',"")
	desktop.setProperty('scanlist5',"")
	desktop.setProperty('scanlist6',"")
	desktop.setProperty('scanlist7',"")
	desktop.setProperty('scanlist8',"")

	status = commands.getstatusoutput('iwgetid -r')
	scanresult = subprocess.Popen(["sudo iwlist wlan0 scan | grep ESSID | cut -d: -f2"], shell=True, stdout=subprocess.PIPE).stdout
	getnetworks = subprocess.Popen(["sudo wpa_cli list_networks | grep any"], shell=True, stdout=subprocess.PIPE).stdout
	linescanresult = scanresult.read().splitlines()
	linegetnetworks = getnetworks.read().splitlines()
	count = 0

	for i in linegetnetworks:
	    count = count + 1
	    values = i.split("\t")
    	    desktop.setProperty('storednet' + str(int(values[0]) + 1),str(values[1]))
    	    desktop.setProperty('storedstate' + str(int(values[0]) + 1),str(values[3]))
	    if str(values[3]) == "[CURRENT]":
    		desktop.setProperty('storedneticon' + str(int(values[0]) + 1),"wifiman_icon_current.png")
		desktop.setProperty('showconfig' + str(int(values[0]) + 1),'true')
	    elif str(values[3]) == "[DISABLED]":
    		desktop.setProperty('storedneticon' + str(int(values[0]) + 1),"wifiman_icon_disabled.png")
		desktop.setProperty('showconfig' + str(int(values[0]) + 1),'true')
	    else:
    		desktop.setProperty('storedneticon' + str(int(values[0]) + 1),"wifiman_icon_ready.png")
		desktop.setProperty('showconfig' + str(int(values[0]) + 1),'true')

	if count == 0:
	    if checkifupdown == "up":
		desktop.setProperty('showconfig1','true')
		desktop.setProperty('clientoffline','false')
	    else:
	    	desktop.setProperty('showconfig1','false')
	    	desktop.setProperty('clientoffline','true')
	    desktop.setProperty('storednet1',"")
	    desktop.setProperty('storedstate1',"")
	    desktop.setProperty('storedneticon1',"")
	    desktop.setProperty('showconfig2','false')
	    desktop.setProperty('storednet2',"")
	    desktop.setProperty('storedstate2',"")
	    desktop.setProperty('storedneticon2',"")
	    desktop.setProperty('showconfig3','false')
	    desktop.setProperty('storednet3',"")
	    desktop.setProperty('storedstate3',"")
	    desktop.setProperty('storedneticon3',"")
	    desktop.setProperty('showconfig4','false')
	    desktop.setProperty('storednet4',"")
	    desktop.setProperty('storedstate4',"")
	    desktop.setProperty('storedneticon4',"")

	if count == 1:
	    desktop.setProperty('showconfig2','true')
	    desktop.setProperty('storednet2',"")
	    desktop.setProperty('storedstate2',"")
	    desktop.setProperty('storedneticon2',"")
	    desktop.setProperty('showconfig3','false')
	    desktop.setProperty('storednet3',"")
	    desktop.setProperty('storedstate3',"")
	    desktop.setProperty('storedneticon3',"")
	    desktop.setProperty('showconfig4','false')
	    desktop.setProperty('storednet4',"")
	    desktop.setProperty('storedstate4',"")
	    desktop.setProperty('storedneticon4',"")

	if count == 2:
	    desktop.setProperty('showconfig3','true')
	    desktop.setProperty('storednet3',"")
	    desktop.setProperty('storedstate3',"")
	    desktop.setProperty('storedneticon3',"")
	    desktop.setProperty('showconfig4','false')
	    desktop.setProperty('storednet4',"")
	    desktop.setProperty('storedstate4',"")
	    desktop.setProperty('storedneticon4',"")

	if count == 3:
	    desktop.setProperty('showconfig4','true')
	    desktop.setProperty('storednet4',"")
	    desktop.setProperty('storedstate4',"")
	    desktop.setProperty('storedneticon4',"")

	count = 1
	networklist = ['[COLOR lightgreen][B]>>> ENABLE NETWORK <<<[/B][/COLOR]','[COLOR orange][B]>>> DISABLE NETWORK <<<[/B][/COLOR]','[COLOR red][B]>>> DELETE NETWORK <<<[/B][/COLOR]','[COLOR blue][B]>>> SELECT NETWORK <<<[/B][/COLOR]','']
	for i in linescanresult:
	    i = str(i.replace('"',''))
	    if i != "":
		if str(i) == str(status[1]):
		    desktop.setProperty('textcolor' + str(count),"lightgreen")
		desktop.setProperty('scanlist' + str(count),str(count) + ': ' + i)
		networklist.append(str(i))
		count = count + 1
	networklist = tuple(networklist)
	desktop.setProperty('startup','false')

	if checkifupdown == "up":
	    desktop.setProperty('showifup','false')
	    desktop.setProperty('showifdown','true')
	    desktop.setProperty('clientoffline','false')
	else:
	    desktop.setProperty('showifup','true')
	    desktop.setProperty('showifdown','false')
	    desktop.setProperty('clientoffline','true')

    else:
	if str(checkifresult[0]) != "wlan0" and len(checkhostapdstate) == 0 and len(checkdnsmasqstate) == 0:
	    desktop.setProperty('wifiavailable','false')
	    desktop.setProperty('hostapdactive','false')
	    desktop.setProperty('scanlist1',"")
	    desktop.setProperty('scanlist2',"")
	    desktop.setProperty('scanlist3',"")
	    desktop.setProperty('scanlist4',"")
	    desktop.setProperty('scanlist5',"")
	    desktop.setProperty('scanlist6',"")
	    desktop.setProperty('scanlist7',"")
	    desktop.setProperty('scanlist8',"")
	    desktop.setProperty('showconfig1','false')
	    desktop.setProperty('storednet1',"")
	    desktop.setProperty('storedstate1',"")
	    desktop.setProperty('storedneticon1',"")
	    desktop.setProperty('showconfig2','false')
	    desktop.setProperty('storednet2',"")
	    desktop.setProperty('storedstate2',"")
	    desktop.setProperty('storedneticon2',"")
	    desktop.setProperty('showconfig3','false')
	    desktop.setProperty('storednet3',"")
	    desktop.setProperty('storedstate3',"")
	    desktop.setProperty('storedneticon3',"")
	    desktop.setProperty('showconfig4','false')
	    desktop.setProperty('storednet4',"")
	    desktop.setProperty('storedstate4',"")
	    desktop.setProperty('storedneticon4',"")

	if str(checkifresult[0]) == "wlan0" and len(checkhostapdstate) != 0 and len(checkdnsmasqstate) != 0:
	    desktop.setProperty('wifiavailable','false')
	    desktop.setProperty('hostapdactive','true')
	    desktop.setProperty('scanlist1',"")
	    desktop.setProperty('scanlist2',"")
	    desktop.setProperty('scanlist3',"")
	    desktop.setProperty('scanlist4',"")
	    desktop.setProperty('scanlist5',"")
	    desktop.setProperty('scanlist6',"")
	    desktop.setProperty('scanlist7',"")
	    desktop.setProperty('scanlist8',"")
	    desktop.setProperty('showconfig1','false')
	    desktop.setProperty('storednet1',"")
	    desktop.setProperty('storedstate1',"")
	    desktop.setProperty('storedneticon1',"")
	    desktop.setProperty('showconfig2','false')
	    desktop.setProperty('storednet2',"")
	    desktop.setProperty('storedstate2',"")
	    desktop.setProperty('storedneticon2',"")
	    desktop.setProperty('showconfig3','false')
	    desktop.setProperty('storednet3',"")
	    desktop.setProperty('storedstate3',"")
	    desktop.setProperty('storedneticon3',"")
	    desktop.setProperty('showconfig4','false')
	    desktop.setProperty('storednet4',"")
	    desktop.setProperty('storedstate4',"")
	    desktop.setProperty('storedneticon4',"")

	    getclients = subprocess.Popen(["sudo cat /var/lib/misc/dnsmasq.leases"], shell=True, stdout=subprocess.PIPE).stdout
	    lineclientresult = getclients.read().splitlines()
	    count = 1
	    if len(lineclientresult) > 0:
		for i in lineclientresult:
		    values = i.split(" ")
		    response = os.system("ping -c1 -t250 " + str(values[2]))
		    if response == 0:
			desktop.setProperty('clientip' + str(count),str(values[3]))
			desktop.setProperty('client' + str(count),str(values[2]))
			count = count + 1
	    while count <= 7:
		desktop.setProperty('clientip' + str(count),'')
		desktop.setProperty('client' + str(count),'')
		count = count + 1
    desktop.setProperty('switching','false')
    desktop.setProperty('startup','false')

def autoScan():
    global timer

    while True:
	if pause != True:
	    timer = timer + 1
	    if timer > 30:
		scanNetworks()
		timer = 0
	time.sleep(0.5)
	if kill == True:
	    break

t1 = Thread( target=autoScan)
t1.setDaemon( True )
t1.start()

class wifimanager(xbmcgui.WindowXMLDialog):

    def onInit(self):
        wifimanager.button_home=self.getControl(HOME_BUTTON)
        wifimanager.button_back=self.getControl(BACK_BUTTON)
        wifimanager.buttonfocus=self.getControl(BUTTON_FOCUS)
        wifimanager.buttonwifi=self.getControl(WIFI_BUTTON)
        wifimanager.buttonapmode=self.getControl(APMODE_BUTTON)
        wifimanager.button_settings=self.getControl(SETTINGS_BUTTON)
        wifimanager.button_connect=self.getControl(CONNECT_BUTTON)
        wifimanager.button_disconnect=self.getControl(DISCONNECT_BUTTON)
	if getrevision() != "RPi3" and addon.getSetting('warning') == "true":
	    xbmcgui.Dialog().ok("$ADDON[plugin.program.wifimanager 30033]","$ADDON[plugin.program.wifimanager 30034]","$ADDON[plugin.program.wifimanager 30035]","$ADDON[plugin.program.wifimanager 30038]")
	checkInstall()

    def onAction(self, action):
    	pass
        
    def onClick(self, controlID):

	global kill, pause, networklist, execute, timer

        if controlID == HOME_BUTTON:
	    self.setFocus(self.buttonfocus)
	    kill = True
	    time.sleep(0.3)
            self.close()

        if controlID == BACK_BUTTON:
	    self.setFocus(self.buttonfocus)
	    kill = True
	    time.sleep(0.3)
            self.close()

        if controlID == DISCONNECT_BUTTON:
	    self.setFocus(self.buttonfocus)
	    pause = True
	    desktop.setProperty('showifdown','false')
	    os.system("sudo /sbin/ifdown wlan0")
	    timer = 28
	    pause = False

        if controlID == SETTINGS_BUTTON:
	    self.setFocus(self.buttonfocus)
	    pause = True
	    addon.openSettings()
	    getrevision()
	    checkInstall()
	    pause = False
	    self.setFocus(self.buttonfocus)

        if controlID == CONNECT_BUTTON:
	    self.setFocus(self.buttonfocus)
	    pause = True
	    desktop.setProperty('showifup','false')
	    os.system("sudo /sbin/ifup wlan0")
	    timer = 28
	    pause = False

        if controlID == NETWORK1_BUTTON:
	    pause = True
	    check = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30001]","$ADDON[plugin.program.wifimanager 30002]")
	    if check == 1:
		selected = xbmcgui.Dialog().select("$ADDON[plugin.program.wifimanager 30003]",networklist)
		if  networklist[selected] != "[COLOR lightgreen][B]>>> ENABLE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR orange][B]>>> DISABLE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR red][B]>>> DELETE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR blue][B]>>> SELECT NETWORK <<<[/B][/COLOR]" and networklist[selected] != "" and selected != -1:
		    password = xbmcgui.Dialog().input("$ADDON[plugin.program.wifimanager 30004]")
		    if password != "":
			os.system("sudo wpa_cli remove_network 0")
			os.system("sudo wpa_cli add_network 0")
			os.system("sudo wpa_cli set_network 0 ssid '\"" + networklist[selected] + "\"'")
			os.system("sudo wpa_cli set_network 0 psk '\"" + password + "\"'")
			os.system("sudo wpa_cli enable_network 0")
			os.system("sudo wpa_cli save")
			desktop.setProperty('storednet1',"...")
		if networklist[selected] == "[COLOR red][B]>>> DELETE NETWORK <<<[/B][/COLOR]":
			really = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30029]","$ADDON[plugin.program.wifimanager 30030]")
			if really == 1:
			    os.system("sudo wpa_cli remove_network 0")
			    os.system("sudo wpa_cli save")
			    desktop.setProperty('showconfig1','false')
			    desktop.setProperty('storednet1',"")
			    desktop.setProperty('storedstate1',"")
			    desktop.setProperty('storedneticon1',"")
			    os.system("sudo wpa_cli reconfigure")
		if networklist[selected] == "[COLOR lightgreen][B]>>> ENABLE NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli enable_network 0")
		if networklist[selected] == "[COLOR orange][B]>>> DISABLE NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli disable_network 0")
		if networklist[selected] == "[COLOR blue][B]>>> SELECT NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli select_network 0")
	    timer = 30
	    pause = False

        if controlID == NETWORK2_BUTTON:
	    pause = True
	    check = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30001]","$ADDON[plugin.program.wifimanager 30002]")
	    if check == 1:
		selected = xbmcgui.Dialog().select("$ADDON[plugin.program.wifimanager 30003]",networklist)
		if  networklist[selected] != "[COLOR lightgreen][B]>>> ENABLE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR orange][B]>>> DISABLE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR red][B]>>> DELETE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR blue][B]>>> SELECT NETWORK <<<[/B][/COLOR]" and networklist[selected] != "" and selected != -1:
		    password = xbmcgui.Dialog().input("$ADDON[plugin.program.wifimanager 30004]")
		    if password != "":
			os.system("sudo wpa_cli remove_network 1")
			os.system("sudo wpa_cli add_network 1")
			os.system("sudo wpa_cli set_network 1 ssid '\"" + networklist[selected] + "\"'")
			os.system("sudo wpa_cli set_network 1 psk '\"" + password + "\"'")
			os.system("sudo wpa_cli enable_network 1")
			os.system("sudo wpa_cli save")
			desktop.setProperty('storednet2',"...")
		if networklist[selected] == "[COLOR red][B]>>> DELETE NETWORK <<<[/B][/COLOR]":
			really = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30029]","$ADDON[plugin.program.wifimanager 30030]")
			if really == 1:
			    os.system("sudo wpa_cli remove_network 1")
			    os.system("sudo wpa_cli save")
			    desktop.setProperty('showconfig2','false')
			    desktop.setProperty('storednet2',"")
			    desktop.setProperty('storedstate2',"")
			    desktop.setProperty('storedneticon2',"")
			    os.system("sudo wpa_cli reconfigure")
		if networklist[selected] == "[COLOR lightgreen][B]>>> ENABLE NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli enable_network 1")
		if networklist[selected] == "[COLOR orange][B]>>> DISABLE NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli disable_network 1")
		if networklist[selected] == "[COLOR blue][B]>>> SELECT NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli select_network 1")
	    timer = 30
	    pause = False

        if controlID == NETWORK3_BUTTON:
	    pause = True
	    check = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30001]","$ADDON[plugin.program.wifimanager 30002]")
	    if check == 1:
		selected = xbmcgui.Dialog().select("$ADDON[plugin.program.wifimanager 30003]",networklist)
		if  networklist[selected] != "[COLOR lightgreen][B]>>> ENABLE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR orange][B]>>> DISABLE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR red][B]>>> DELETE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR blue][B]>>> SELECT NETWORK <<<[/B][/COLOR]" and networklist[selected] != "" and selected != -1:
		    password = xbmcgui.Dialog().input("$ADDON[plugin.program.wifimanager 30004]")
		    if password != "":
			os.system("sudo wpa_cli remove_network 2")
			os.system("sudo wpa_cli add_network 2")
			os.system("sudo wpa_cli set_network 2 ssid '\"" + networklist[selected] + "\"'")
			os.system("sudo wpa_cli set_network 2 psk '\"" + password + "\"'")
			os.system("sudo wpa_cli enable_network 2")
			os.system("sudo wpa_cli save")
			desktop.setProperty('storednet3',"...")
		if networklist[selected] == "[COLOR red][B]>>> DELETE NETWORK <<<[/B][/COLOR]":
			really = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30029]","$ADDON[plugin.program.wifimanager 30030]")
			if really == 1:
			    os.system("sudo wpa_cli remove_network 2")
			    os.system("sudo wpa_cli save")
			    desktop.setProperty('showconfig3','false')
			    desktop.setProperty('storednet3',"")
			    desktop.setProperty('storedstate3',"")
			    desktop.setProperty('storedneticon3',"")
			    os.system("sudo wpa_cli reconfigure")
		if networklist[selected] == "[COLOR lightgreen][B]>>> ENABLE NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli enable_network 2")
			scanNetworks()
		if networklist[selected] == "[COLOR orange][B]>>> DISABLE NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli disable_network 2")
		if networklist[selected] == "[COLOR blue][B]>>> SELECT NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli select_network 2")
	    timer = 30
	    pause = False

        if controlID == NETWORK4_BUTTON:
	    pause = True
	    check = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30001]","$ADDON[plugin.program.wifimanager 30002]")
	    if check == 1:
		selected = xbmcgui.Dialog().select("$ADDON[plugin.program.wifimanager 30003]",networklist)
		if  networklist[selected] != "[COLOR lightgreen][B]>>> ENABLE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR orange][B]>>> DISABLE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR red][B]>>> DELETE NETWORK <<<[/B][/COLOR]" and networklist[selected] != "[COLOR blue][B]>>> SELECT NETWORK <<<[/B][/COLOR]" and networklist[selected] != "" and selected != -1:
		    password = xbmcgui.Dialog().input("$ADDON[plugin.program.wifimanager 30004]")
		    if password != "":
			os.system("sudo wpa_cli remove_network 3")
			os.system("sudo wpa_cli add_network 3")
			os.system("sudo wpa_cli set_network 3 ssid '\"" + networklist[selected] + "\"'")
			os.system("sudo wpa_cli set_network 3 psk '\"" + password + "\"'")
			os.system("sudo wpa_cli enable_network 3")
			os.system("sudo wpa_cli save")
			desktop.setProperty('storednet4',"...")
		if networklist[selected] == "[COLOR red][B]>>> DELETE NETWORK <<<[/B][/COLOR]":
			really = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30029]","$ADDON[plugin.program.wifimanager 30030]")
			if really == 1:
			    os.system("sudo wpa_cli remove_network 3")
			    os.system("sudo wpa_cli save")
			    desktop.setProperty('storednet4',"...")
			    desktop.setProperty('storedstate4',"")
			    desktop.setProperty('storedneticon4',"")
			    os.system("sudo wpa_cli reconfigure")
		if networklist[selected] == "[COLOR lightgreen][B]>>> ENABLE NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli enable_network 3")
		if networklist[selected] == "[COLOR orange][B]>>> DISABLE NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli disable_network 3")
		if networklist[selected] == "[COLOR blue][B]>>> SELECT NETWORK <<<[/B][/COLOR]":
			os.system("sudo wpa_cli select_network 3")
	    timer = 30
	    pause = False

        if controlID == WIFI_BUTTON:
	    pause = True
	    self.setFocus(self.buttonfocus)
	    desktop.setProperty('switching','true')
	    time.sleep(1)
	    if execute == False:
		execcute = True
		desktop.setProperty('wifiavailable','true')
		run_command("sudo /etc/init.d/dnsmasq stop")
		time.sleep(0.5)
		run_command("sudo /etc/init.d/hostapd stop")
		time.sleep(1)
		desktop.setProperty('commandoutput',"Stopping interface wlan0...")
		run_command("sudo /sbin/ifdown wlan0")
		time.sleep(0.5)
		desktop.setProperty('commandoutput',"Starting interface wlan0...")
		run_command("sudo /sbin/ifup wlan0")
		time.sleep(0.5)
		desktop.setProperty('commandoutput',"Reconfigure IP by dhclient...")
		run_command("sudo /sbin/dhclient -r")
		time.sleep(0.5)
		desktop.setProperty('hostapdactive','false')
		desktop.setProperty('commandoutput',"")
		timer = 25
		pause = False
		execute = False

        if controlID == APMODE_BUTTON:
	    pause = True
	    self.setFocus(self.buttonfocus)
	    desktop.setProperty('switching','true')
	    desktop.setProperty('showifup','false')
	    desktop.setProperty('showifdown','false')
	    time.sleep(1)
	    if execute == False:
		execcute = True
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
		timer = 28
		pause = False
		execute = False

        if controlID == HOSTAPD_BUTTON:
	    self.setFocus(self.buttonfocus)
	    restart = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30031]","$ADDON[plugin.program.wifimanager 30032]")
	    if restart == 1:
		pause = True
		if execute == False:
		    desktop.setProperty('hostapdicon',"wifiman_icon_ready.png")
		    execcute = True
		    count = 1
		    while count <= 7:
			desktop.setProperty('clientip' + str(count),'')
			desktop.setProperty('client' + str(count),'')
			count = count + 1
		    os.system("sudo /etc/init.d/hostapd restart")
		    execcute = False
		    timer = 30
		    pause = False

        if controlID == DNSMASQ_BUTTON:
	    self.setFocus(self.buttonfocus)
	    restart = xbmcgui.Dialog().yesno("$ADDON[plugin.program.wifimanager 30031]","$ADDON[plugin.program.wifimanager 30032]")
	    if restart == 1:
		pause = True
		if execute == False:
		    desktop.setProperty('dnsmasqicon',"wifiman_icon_ready.png")
		    execcute = True
		    os.system("sudo /etc/init.d/dnsmasq restart")
		    execcute = False
		    timer = 30
		    pause = False

    def onFocus(self, controlID):
        pass
    
    def onControl(self, controlID):
        pass

wifimanagerdialog = wifimanager("Custom_WIFIManager.xml", addonpath, 'default', '720')
wifimanagerdialog.doModal()
del wifimanagerdialog


