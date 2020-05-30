#
#      Original by Brian Wallen [bwallen@gmail.com]
# 	   Updated & Modified by Andreas [thix@gmx.net]
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html


import datetime
import threading

import time

import xbmc
import xbmcgui

from notification import Notification
from strings import *

from pyobd2 import obd_io
from pyobd2 import obd_sensors

DEBUG = 1

ACTION_MOUSE_WHEEL_UP = 104
ACTION_MOUSE_WHEEL_DOWN = 105
ACTION_MOUSE_MOVE = 107
KEY_NAV_BACK = 92
ACTION_PARENT_DIR = 9

ADDON = xbmcaddon.Addon(id = 'script.cardiagnostic')

THREADS = []

def debug(s):
	xbmc.log("[script.cardiagnostic] - " + str(s))

class Point(object):
	def __init__(self):
		self.x = self.y = 0

	def __repr__(self):
		return 'Point(x=%d, y=%d)' % (self.x, self.y)

class SerialInitializer(threading.Thread):
	def __init__(self, sourceInitializedHandler):
		super(SerialInitializer, self).__init__()
		self.sourceInitializedHandler = sourceInitializedHandler
		self._stop = threading.Event()

	def run(self):
		i=0
		while not xbmc.abortRequested or self.stopped() == True:
			debug("serialinit " + str(self.stopped()))
			try:
				debug("Opening Port")
				if not ADDON.getSetting('device'):
					xbmcgui.Dialog().ok("Device", "Please set your device name")
					ADDON.openSettings()
				if not ADDON.getSetting('baud'):
					xbmcgui.Dialog().ok("Baud", "Please set your baud rate (default: 9600)")
					ADDON.openSettings()
				self.port = obd_io.OBDPort(ADDON.getSetting('device'),ADDON.getSetting('baud'))
				self.sensorresults={}
				debug("Device Opened")
				self.sourceInitializedHandler.onPortInitialized()
				break
			except Exception as e:
				debug("Attempt " + str(i) + " failed to open serial port - " + str(e))
				i+=1
				if i == 5:
					xbmcgui.Dialog().ok("Port Failed", "Couldn't connect to serial device after 5 attempts")
					debug("got here")
					self.port = ''
					self.sourceInitializedHandler.onPortInitialized()
					break
					time.sleep(5)

	def stop(self):
		self.port.close()
		debug("stopped serialinit - " + self.name)
		self._stop.set()
	
	def stopped(self):
		return self._stop.isSet()

class ControlAndProgram(object):
	def __init__(self, control, program):
		self.control = control
		self.program = program

class Dashboard1(threading.Thread):
	def __init__(self, dashboard1):
		super(Dashboard1, self).__init__()
		self.dashboard1 = dashboard1
		self._stop = threading.Event()
	
	def updateMediaInfo(self):
		info = self.player.getMusicInfoTag()
		self.dashboard1.setControlLabel(self.dashboard1.C_MEDIA_SONG, str(info.getArtist() + " - " + info.getTitle()))
		
	def run(self):
		self.player = xbmc.Player()
					
		debug("running dashboard1 class")
		self.dashboard1._showControl(self.dashboard1.C_DASHBOARD)
		if self.dashboard1.serial.port == '':
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_TITLE, "Failed to open port")
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_SPEED, "0")
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_RPM, "0")
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_INTAKE_PRES, "0")
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_INTAKE_TEMP, "0")
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_MAF, "0")
			
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_COOLANT_TEMP, "0")
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_ENGINE_LOAD, "0")
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_THROTTLE, "0")
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_FUEL, "0")
			
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_ACCELERATOR, "0")
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_AMBIENT_TEMP, "0")
			
			self.dashboard1.setControlLabel(self.dashboard1.C_MAIN_CLEAR_DTCS, "0")
			
			while xbmc.abortRequested or not self.stopped():
				if self.player.isPlayingAudio():
					self.updateMediaInfo()
					
		else:
			self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_TITLE, "carDiagnostic")
			

			#self.debugAll()

			
		
			while xbmc.abortRequested or not self.stopped():
				if self.player.isPlayingAudio():
					self.updateMediaInfo()

				# Get and display speed
				self.dashboard1.serial.port.send_command("010D")
				speed = self.dashboard1.serial.port.get_result()
				self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_SPEED, str(obd_sensors.speed(speed)))

				# Get and display RPM
				self.dashboard1.serial.port.send_command("010C")
				rpm = self.dashboard1.serial.port.get_result()
				self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_RPM, str(obd_sensors.rpm(rpm)))

				# Get and display Intake Temp
				self.dashboard1.serial.port.send_command("010F")
				intake_temp = self.dashboard1.serial.port.get_result()
				self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_INTAKE_TEMP, str(obd_sensors.temp(intake_temp)))

				# Get and display Intake MAF
				self.dashboard1.serial.port.send_command("0110")
				maf = self.dashboard1.serial.port.get_result()
				self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_MAF, str(obd_sensors.maf(maf)))
				
				# Get and display Coolant Temp
				self.dashboard1.serial.port.send_command("0105")
				coolant_temp = self.dashboard1.serial.port.get_result()
				self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_COOLANT_TEMP, str(obd_sensors.temp(coolant_temp)))
				
				# Get and display Engine Load
				self.dashboard1.serial.port.send_command("0104")
				engine_load = self.dashboard1.serial.port.get_result()
				self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_ENGINE_LOAD, str(obd_sensors.percent_scale(engine_load)))
				
				# Get intake pressure
				self.dashboard1.serial.port.send_command("010B")
				intake_pres = self.dashboard1.serial.port.get_result()
				self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_INTAKE_PRES, str(obd_sensors.intake_m_pres(intake_pres)))
				
				# Get throttle position
				self.dashboard1.serial.port.send_command("0111")
				throttle_pos = self.dashboard1.serial.port.get_result()
				self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_THROTTLE, str(obd_sensors.throttle_pos(throttle_pos)))
				
				# Get Accelerator pedal position - NO DATA 
				#self.dashboard1.serial.port.send_command("015A")
				#accel_pos = self.dashboard1.serial.port.get_result()
				#self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_ACCELERATOR, str(obd_sensors.voltage(accel_pos)))
				
				# Get Ambient Temperature - NO DATA 
				#self.dashboard1.serial.port.send_command("0146")
				#ambient_temp = self.dashboard1.serial.port.get_result()
				#self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_AMBIENT_TEMP, str(obd_sensors.temp(ambient_temp)))
				
				# FUEL RATE - NO DATA 
				#self.dashboard1.serial.port.send_command("015E")
				#run = self.dashboard1.serial.port.get_result()
				#self.dashboard1.setControlLabel(self.dashboard1.C_DASHBOARD_FUEL, str(obd_sensors.fuel_rate(run)))
				
				# Get and display supported DTCs
				DTCs = self.dashboard1.serial.port.get_dtc()
				debug ("DTCs var: " + DTCs)
				self.dashboard1.setControlLabel(self.dashboard1.C_MAIN_CLEAR_DTCS, str(len(DTCs)))	
				
				time.sleep(.2)
	
	def debugAll(self):
		self.dashboard1.serial.port.send_command("0101")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0101\t"+ check_val)
		self.dashboard1.serial.port.send_command("0102")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0102\t"+ check_val)
		self.dashboard1.serial.port.send_command("0103")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0103\t"+ check_val)
		self.dashboard1.serial.port.send_command("0104")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0104\t"+ check_val)
		self.dashboard1.serial.port.send_command("0105")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0105\t"+ check_val)
		self.dashboard1.serial.port.send_command("0106")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0106\t"+ check_val)
		self.dashboard1.serial.port.send_command("0107")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0107\t"+ check_val)
		self.dashboard1.serial.port.send_command("0108")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0108\t"+ check_val)
		self.dashboard1.serial.port.send_command("0109")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0109\t"+ check_val)
		self.dashboard1.serial.port.send_command("010A")
		check_val = self.dashboard1.serial.port.get_result()
		debug("010A\t"+ check_val)
		self.dashboard1.serial.port.send_command("010B")
		check_val = self.dashboard1.serial.port.get_result()
		debug("010B\t"+ check_val)
		self.dashboard1.serial.port.send_command("010C")
		check_val = self.dashboard1.serial.port.get_result()
		debug("010C\t"+ check_val)
		self.dashboard1.serial.port.send_command("010D")
		check_val = self.dashboard1.serial.port.get_result()
		debug("010D\t"+ check_val)
		self.dashboard1.serial.port.send_command("010E")
		check_val = self.dashboard1.serial.port.get_result()
		debug("010E\t"+ check_val)
		self.dashboard1.serial.port.send_command("010F")
		check_val = self.dashboard1.serial.port.get_result()
		debug("010F\t"+ check_val)
		self.dashboard1.serial.port.send_command("0110")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0110\t"+ check_val)
		self.dashboard1.serial.port.send_command("0111")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0111\t"+ check_val)
		self.dashboard1.serial.port.send_command("0112")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0112\t"+ check_val)
		self.dashboard1.serial.port.send_command("0113")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0113\t"+ check_val)
		self.dashboard1.serial.port.send_command("0114")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0114\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0115")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0115\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0116")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0116\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0117")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0117\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0118")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0118\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0119")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0119\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("011A")
		check_val = self.dashboard1.serial.port.get_result()
		debug("011A\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("011B")
		check_val = self.dashboard1.serial.port.get_result()
		debug("011B\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("011C")
		check_val = self.dashboard1.serial.port.get_result()
		debug("011C\t"+ check_val)
		self.dashboard1.serial.port.send_command("011D")
		check_val = self.dashboard1.serial.port.get_result()
		debug("011D\t"+ check_val)
		self.dashboard1.serial.port.send_command("011E")
		check_val = self.dashboard1.serial.port.get_result()
		debug("011E\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("011F")
		check_val = self.dashboard1.serial.port.get_result()
		debug("011F\t"+ check_val)
		self.dashboard1.serial.port.send_command("0120")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0120\t"+ check_val)
		self.dashboard1.serial.port.send_command("0121")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0121\t"+ check_val)
		self.dashboard1.serial.port.send_command("0122")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0122\t"+ check_val)
		self.dashboard1.serial.port.send_command("0123")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0123\t"+ check_val)
		self.dashboard1.serial.port.send_command("0124")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0124\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0125")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0125\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0126")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0126\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0127")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0127\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0128")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0128\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0129")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0129\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("012A")
		check_val = self.dashboard1.serial.port.get_result()
		debug("012A\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("012B")
		check_val = self.dashboard1.serial.port.get_result()
		debug("012B\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("012C")
		check_val = self.dashboard1.serial.port.get_result()
		debug("012C\t"+ check_val)
		self.dashboard1.serial.port.send_command("012D")
		check_val = self.dashboard1.serial.port.get_result()
		debug("012D\t"+ check_val)
		self.dashboard1.serial.port.send_command("012E")
		check_val = self.dashboard1.serial.port.get_result()
		debug("012E\t"+ check_val)
		self.dashboard1.serial.port.send_command("012F")
		check_val = self.dashboard1.serial.port.get_result()
		debug("012F\t"+ check_val)
		self.dashboard1.serial.port.send_command("0130")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0130\t"+ check_val)
		self.dashboard1.serial.port.send_command("0131")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0131\t"+ check_val)
		self.dashboard1.serial.port.send_command("0132")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0132\t"+ check_val)
		self.dashboard1.serial.port.send_command("0133")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0133\t"+ check_val)
		self.dashboard1.serial.port.send_command("0134")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0134\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0135")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0135\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0136")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0136\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0137")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0137\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0138")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0138\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0139")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0139\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("013A")
		check_val = self.dashboard1.serial.port.get_result()
		debug("013A\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("013B")
		check_val = self.dashboard1.serial.port.get_result()
		debug("013B\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("013C")
		check_val = self.dashboard1.serial.port.get_result()
		debug("013C\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("013D")
		check_val = self.dashboard1.serial.port.get_result()
		debug("013D\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("013E")
		check_val = self.dashboard1.serial.port.get_result()
		debug("013E\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("013F")
		check_val = self.dashboard1.serial.port.get_result()
		debug("013F\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0140")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0140\t"+ check_val)
		self.dashboard1.serial.port.send_command("0141")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0141\t"+ check_val)
		self.dashboard1.serial.port.send_command("0142")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0142\t"+ check_val)
		self.dashboard1.serial.port.send_command("0143")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0143\t"+ check_val)
		self.dashboard1.serial.port.send_command("0144")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0144\t"+ check_val)
		self.dashboard1.serial.port.send_command("0145")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0145\t"+ check_val)
		self.dashboard1.serial.port.send_command("0146")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0146\t"+ check_val)
		self.dashboard1.serial.port.send_command("0147")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0147\t"+ check_val)
		self.dashboard1.serial.port.send_command("0148")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0148\t"+ check_val)
		self.dashboard1.serial.port.send_command("0149")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0149\t"+ check_val)
		self.dashboard1.serial.port.send_command("014A")
		check_val = self.dashboard1.serial.port.get_result()
		debug("014A\t"+ check_val)
		self.dashboard1.serial.port.send_command("014B")
		check_val = self.dashboard1.serial.port.get_result()
		debug("014B\t"+ check_val)
		self.dashboard1.serial.port.send_command("014C")
		check_val = self.dashboard1.serial.port.get_result()
		debug("014C\t"+ check_val)
		self.dashboard1.serial.port.send_command("014D")
		check_val = self.dashboard1.serial.port.get_result()
		debug("014D\t"+ check_val)
		self.dashboard1.serial.port.send_command("014E")
		check_val = self.dashboard1.serial.port.get_result()
		debug("014E\t"+ check_val)
		self.dashboard1.serial.port.send_command("014F")
		check_val = self.dashboard1.serial.port.get_result()
		debug("014F\t"+ check_val)
		self.dashboard1.serial.port.send_command("0150")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0150\t"+ check_val)
		self.dashboard1.serial.port.send_command("0151")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0151\t"+ check_val)
		self.dashboard1.serial.port.send_command("0152")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0152\t"+ check_val)
		self.dashboard1.serial.port.send_command("0153")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0153\t"+ check_val)
		self.dashboard1.serial.port.send_command("0154")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0154\t"+ check_val)
		self.dashboard1.serial.port.send_command("0155")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0155\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0156")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0156\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0157")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0157\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0158")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0158\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0159")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0159\t"+ check_val)
		self.dashboard1.serial.port.send_command("015A")
		check_val = self.dashboard1.serial.port.get_result()
		debug("015A\t"+ check_val)
		self.dashboard1.serial.port.send_command("015B")
		check_val = self.dashboard1.serial.port.get_result()
		debug("015B\t"+ check_val)
		self.dashboard1.serial.port.send_command("015C")
		check_val = self.dashboard1.serial.port.get_result()
		debug("015C\t"+ check_val)
		self.dashboard1.serial.port.send_command("015D")
		check_val = self.dashboard1.serial.port.get_result()
		debug("015D\t"+ check_val)
		self.dashboard1.serial.port.send_command("015E")
		check_val = self.dashboard1.serial.port.get_result()
		debug("015E\t"+ check_val)
		self.dashboard1.serial.port.send_command("015F")
		check_val = self.dashboard1.serial.port.get_result()
		debug("015F\t"+ check_val)
		self.dashboard1.serial.port.send_command("0160")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0160\t"+ check_val)
		self.dashboard1.serial.port.send_command("0161")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0161\t"+ check_val)
		self.dashboard1.serial.port.send_command("0162")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0162\t"+ check_val)
		self.dashboard1.serial.port.send_command("0163")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0163\t"+ check_val)
		self.dashboard1.serial.port.send_command("0164")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0164\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)
		self.dashboard1.serial.port.send_command("0165")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0165\t"+ check_val)
		self.dashboard1.serial.port.send_command("0166")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0166\t"+ check_val)
		self.dashboard1.serial.port.send_command("0167")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0167\t"+ check_val)
		self.dashboard1.serial.port.send_command("0168")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0168\t"+ check_val)
		self.dashboard1.serial.port.send_command("0169")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0169\t"+ check_val)
		self.dashboard1.serial.port.send_command("016A")
		check_val = self.dashboard1.serial.port.get_result()
		debug("016A\t"+ check_val)
		self.dashboard1.serial.port.send_command("016B")
		check_val = self.dashboard1.serial.port.get_result()
		debug("016B\t"+ check_val)
		self.dashboard1.serial.port.send_command("016C")
		check_val = self.dashboard1.serial.port.get_result()
		debug("016C\t"+ check_val)
		self.dashboard1.serial.port.send_command("016D")
		check_val = self.dashboard1.serial.port.get_result()
		debug("016D\t"+ check_val)
		self.dashboard1.serial.port.send_command("016E")
		check_val = self.dashboard1.serial.port.get_result()
		debug("016E\t"+ check_val)
		self.dashboard1.serial.port.send_command("016F")
		check_val = self.dashboard1.serial.port.get_result()
		debug("016F\t"+ check_val)
		self.dashboard1.serial.port.send_command("0170")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0170\t"+ check_val)
		self.dashboard1.serial.port.send_command("0171")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0171\t"+ check_val)
		self.dashboard1.serial.port.send_command("0172")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0172\t"+ check_val)
		self.dashboard1.serial.port.send_command("0173")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0173\t"+ check_val)
		self.dashboard1.serial.port.send_command("0174")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0174\t"+ check_val)
		self.dashboard1.serial.port.send_command("0175")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0175\t"+ check_val)
		self.dashboard1.serial.port.send_command("0176")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0176\t"+ check_val)
		self.dashboard1.serial.port.send_command("0177")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0177\t"+ check_val)
		self.dashboard1.serial.port.send_command("0178")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0178\t"+ check_val)
		self.dashboard1.serial.port.send_command("0179")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0179\t"+ check_val)
		self.dashboard1.serial.port.send_command("017A")
		check_val = self.dashboard1.serial.port.get_result()
		debug("017A\t"+ check_val)
		self.dashboard1.serial.port.send_command("017B")
		check_val = self.dashboard1.serial.port.get_result()
		debug("017B\t"+ check_val)
		self.dashboard1.serial.port.send_command("017C")
		check_val = self.dashboard1.serial.port.get_result()
		debug("017C\t"+ check_val)
		self.dashboard1.serial.port.send_command("017D")
		check_val = self.dashboard1.serial.port.get_result()
		debug("017D\t"+ check_val)
		self.dashboard1.serial.port.send_command("017E")
		check_val = self.dashboard1.serial.port.get_result()
		debug("017E\t"+ check_val)
		self.dashboard1.serial.port.send_command("017F")
		check_val = self.dashboard1.serial.port.get_result()
		debug("017F\t"+ check_val)
		self.dashboard1.serial.port.send_command("0180")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0180\t"+ check_val)
		self.dashboard1.serial.port.send_command("0181")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0181\t"+ check_val)
		self.dashboard1.serial.port.send_command("0182")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0182\t"+ check_val)
		self.dashboard1.serial.port.send_command("0183")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0183\t"+ check_val)
		self.dashboard1.serial.port.send_command("0184")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0184\t"+ check_val)
		self.dashboard1.serial.port.send_command("0185")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0185\t"+ check_val)
		self.dashboard1.serial.port.send_command("0186")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0186\t"+ check_val)
		self.dashboard1.serial.port.send_command("0187")
		check_val = self.dashboard1.serial.port.get_result()
		debug("0187\t"+ check_val)
		self.dashboard1.serial.port.send_command("01A0")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01A0\t"+ check_val)
		self.dashboard1.serial.port.send_command("01C0")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01C0\t"+ check_val)
		self.dashboard1.serial.port.send_command("01C3")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01C3\t"+ check_val)
		self.dashboard1.serial.port.send_command("01C4")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01C4\t"+ check_val)
		self.dashboard1.serial.port.send_command("01")
		check_val = self.dashboard1.serial.port.get_result()
		debug("01\t"+ check_val)

	
	def stop(self):
		self._stop.set()
		debug("set dashboard stop - " + self.name)
	
	def stopped(self):
		return self._stop.isSet()
		
class obd2(xbmcgui.WindowXML):
	C_MAIN_LOADING = 4200
	C_MAIN_LOADING_PROGRESS = 4201
	C_MAIN_LOADING_TIME_LEFT = 4202
	C_MAIN_LOADING_CANCEL = 4203
	C_MAIN_MOUSE_CONTROLS = 4300
	C_MEDIA_SONG = 4301
	C_MEDIA_ARTIST = 4302
	C_MEDIA_PREV_TRACK = 4304
	C_MEDIA_NEXT_TRACK = 4305
	C_MAIN_MOUSE_EXIT = 4306
	C_MAIN_BACKGROUND = 4600
	C_MAIN_OSD = 5000
	C_DASHBOARD = 10000
	C_DASHBOARD_TITLE = 10001
	C_DASHBOARD_SPEED = 10003
	C_DASHBOARD_RPM = 10005
	C_DASHBOARD_FUEL = 10021
	C_DASHBOARD_THROTTLE = 10019
	C_DASHBOARD_INTAKE_PRES = 10007
	C_DASHBOARD_INTAKE_TEMP = 10009
	C_DASHBOARD_DTCS = 10011
	C_DASHBOARD_MAF = 10013
	C_DASHBOARD_COOLANT_TEMP = 10015
	C_DASHBOARD_ENGINE_LOAD = 10017
	C_DASHBOARD_AMBIENT_TEMP = 10025
	C_DASHBOARD_ACCELERATOR = 10023
	
	C_MAIN_CLEAR_DTCS = 10100

	def __new__(cls):
		return super(obd2, cls).__new__(cls, 'script-cardiagnostic-main.xml', ADDON.getAddonInfo('path'))

	def __init__(self):
		super(obd2, self).__init__()
		self.redrawingOSD = False
		self.isClosing = False
		#self._stop = threading.Event()
		self.focusPoint = Point()
		self.controlAndProgramList = list()
		self.ignoreMissingControlIds = list()

		# add and removeControls were added post-eden
		self.hasAddControls = hasattr(self, 'addControls')
		self.hasRemoveControls = hasattr(self, 'removeControls')

		
	def getControl(self, controlId):
		try:
			return super(obd2, self).getControl(controlId)
		except TypeError:
			if controlId in self.ignoreMissingControlIds:
				return None
			if not self.isClosing:
				self.close()
			return None

	def close(self):
		if not self.isClosing:
			self.isClosing = True
			self.dashboard1.stop()
			#self.serial.stop()
			for T in THREADS:
				debug("joining")
				T.join()
			super(obd2, self).close()

	def onInit(self):
		self._hideControl(self.C_MAIN_MOUSE_CONTROLS, self.C_MAIN_OSD)
		self._showControl(self.C_MAIN_OSD, self.C_MAIN_LOADING)
		self.setControlLabel(self.C_MAIN_LOADING_TIME_LEFT, strings(BACKGROUND_UPDATE_IN_PROGRESS))
		self.setFocusId(self.C_MAIN_LOADING_CANCEL)

		self.serial = SerialInitializer(self)
		self.serial.start()
		THREADS.append(self.serial)
	
		self._showControl(self.C_MAIN_MOUSE_CONTROLS)

	def onAction(self, action):
		if action.getId() in [ACTION_PARENT_DIR, KEY_NAV_BACK]:
			self.close()
			return

		elif action.getId() == ACTION_MOUSE_MOVE:
			self._showControl(self.C_MAIN_MOUSE_CONTROLS)
			return

		controlInFocus = None
		currentFocus = self.focusPoint
		try:
			controlInFocus = self.getFocus()
			if controlInFocus in [elem.control for elem in self.controlAndProgramList]:
				(left, top) = controlInFocus.getPosition()
				currentFocus = Point()
				currentFocus.x = left + (controlInFocus.getWidth() / 2)
				currentFocus.y = top + (controlInFocus.getHeight() / 2)
		except Exception:
			control = self._findControlAt(self.focusPoint)
			if control is None and len(self.controlAndProgramList) > 0:
				control = self.controlAndProgramList[0].control
			if control is not None:
				self.setFocus(control)
				return

		
	def onClick(self, controlId):
		if controlId in [self.C_MAIN_LOADING_CANCEL, self.C_MAIN_MOUSE_EXIT]:
			self.close()
			debug("close! :)")
			
		elif controlId in [self.C_MAIN_CLEAR_DTCS]:
			self.showDTC()
			return

		if self.isClosing:
			return

		elif controlId == self.C_MEDIA_NEXT_TRACK:
			xbmc.Player().playnext()
			return
		elif controlId == self.C_MEDIA_PREV_TRACK:
			xbmc.Player().playprevious()
			return
			
		else:
			return

	def showDTC(self):
	
		DTCs = self.serial.port.get_dtc()
		#DTCs = ['aba', 'xyz', 'xgx', 'dssd', 'sdjh']
		strDTCs = ""
		for DTC in DTCs:
			strDTCs = strDTCs + "\n" + DTC + " " #+ obd_sensors.dtc_decrypt(DTC)
			
		ret = xbmcgui.Dialog().yesno("DTC", "Do you want to clear all DTC?\n" + strDTCs)
		if ret:
			self.serial.port.clear_dtc
			debug("cleared DTCs")
			
			
	
	
	def setFocusId(self, controlId):
		control = self.getControl(controlId)
		if control:
			self.setFocus(control)

	def setFocus(self, control):
		debug('setFocus %d' % control.getId())
		if control in [elem.control for elem in self.controlAndProgramList]:
			debug('Focus before %s' % self.focusPoint)
			(left, top) = control.getPosition()
			if left > self.focusPoint.x or left + control.getWidth() < self.focusPoint.x:
				self.focusPoint.x = left
			self.focusPoint.y = top + (control.getHeight() / 2)
			debug('New focus at %s' % self.focusPoint)

		super(obd2, self).setFocus(control)

	def onFocus(self, controlId):
		try:
			controlInFocus = self.getControl(controlId)
		except Exception:
			return


		
	def onRedrawOSD(self, focusFunction = None):
		if self.redrawingOSD or self.isClosing:
			debug('onRedrawOSD - already redrawing')
			return # ignore redraw request while redrawing
		debug('onRedrawOSD')
		#self._showControl(self.C_MAIN_TEST)
		#if self.serial.port:
			#self.serial.port.send_command("at@1")   # initialize
			#scantool = self.serial.port.get_result()
			#self.setControlLabel(self.C_DASHBOARD_TITLE, scantool)
			#time.sleep(5)
		#else:
		#	self.setControlLabel(self.C_DASHBOARD_TITLE, "Failed to open Port")

		self.redrawingOSD = True
		self._showControl(self.C_MAIN_OSD)

		# show Loading screen
		self.setControlLabel(self.C_MAIN_LOADING_TIME_LEFT, strings(CALCULATING_REMAINING_TIME))
		self._showControl(self.C_MAIN_LOADING)
		self.setFocusId(self.C_MAIN_LOADING_CANCEL)

		# remove existing controls
		self._clearOsd()

		self._hideControl(self.C_MAIN_LOADING)
		self.dashboard1 = Dashboard1(self)
		self.dashboard1.start()
		THREADS.append(self.dashboard1)
		self.redrawingOSD = False

	def _clearOsd(self):
		if self.hasRemoveControls:
			controls = [elem.control for elem in self.controlAndProgramList]
			try:
				self.removeControls(controls)
			except RuntimeError:
				for elem in self.controlAndProgramList:
					try:
						self.removeControl(elem.control)
					except RuntimeError:
						pass # happens if we try to remove a control that doesn't exist
		else:
			for elem in self.controlAndProgramList:
				try:
					self.removeControl(elem.control)
				except RuntimeError:
					pass # happens if we try to remove a control that doesn't exist
		del self.controlAndProgramList[:]

	
	def onSourceProgressUpdate(self, percentageComplete):
		control = self.getControl(self.C_MAIN_LOADING_PROGRESS)
		if percentageComplete < 1:
			if control:
				control.setPercent(1)
			self.progressStartTime = datetime.datetime.now()
			self.progressPreviousPercentage = percentageComplete
		elif percentageComplete != self.progressPreviousPercentage:
			if control:
				control.setPercent(percentageComplete)
			self.progressPreviousPercentage = percentageComplete
			delta = datetime.datetime.now() - self.progressStartTime

			if percentageComplete < 20:
				self.setControlLabel(self.C_MAIN_LOADING_TIME_LEFT, strings(CALCULATING_REMAINING_TIME))
			else:
				secondsLeft = int(delta.seconds) / float(percentageComplete) * (100.0 - percentageComplete)
				if secondsLeft > 30:
					secondsLeft -= secondsLeft % 10
				self.setControlLabel(self.C_MAIN_LOADING_TIME_LEFT, strings(TIME_LEFT) % secondsLeft)

		return not xbmc.abortRequested and not self.isClosing


	def onPortInitialized(self):
		self.onRedrawOSD()

	def _findControlAt(self, point):
		for elem in self.controlAndProgramList:
			control = elem.control
			(left, top) = control.getPosition()
			bottom = top + control.getHeight()
			right = left + control.getWidth()

			if left <= point.x <= right and  top <= point.y <= bottom:
				return control

		return None

	def _hideControl(self, *controlIds):
		"""
		Visibility is inverted in skin
		"""
		for controlId in controlIds:
			control = self.getControl(controlId)
			if control:
				control.setVisible(True)

	def _showControl(self, *controlIds):
		"""
		Visibility is inverted in skin
		"""
		for controlId in controlIds:
			control = self.getControl(controlId)
			if control:
				control.setVisible(False)

	def setControlImage(self, controlId, image):
		control = self.getControl(controlId)
		if control:
			control.setImage(image)

	def setControlLabel(self, controlId, label):
		control = self.getControl(controlId)
		if control:
			control.setLabel(label)

	def setControlText(self, controlId, text):
		control = self.getControl(controlId)
		if control:
			control.setText(text)
