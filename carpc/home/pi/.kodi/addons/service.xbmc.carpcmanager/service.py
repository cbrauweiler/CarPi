import xbmc
import xbmcgui
import time
import os
import socket


print "Starting Car PC Manager"


SLOW_DOWN_FACTOR = 50.0
DEFAULT_TIMEOUT = 0.1
FLICK_Y_MAX_DISTANCE = 400.0 # maximum distance in pixels a user can flick on the Y axis
FLICK_MIN_TIMEOUT = 0.16 # the minimum timeout(in a short flick)

MB_NONE 		= 0 # no action should occur
MB_SHORT_CLICK 	= 1 # a short click has occurred (a double click may be in process)
MB_LONG_CLICK 	= 2 # a long click has occurred
MB_DOUBLE_CLICK = 3 # a double click has occurred
MB_DRAG_START 	= 4 # a drag action has started
MB_DRAG 		= 5 # a drag action is in progress
MB_DRAG_END 	= 6 # a drag action has finished

holdCount = 0
canHold = 0
posX = 0
posY = 0
dragging = 0
timeout = DEFAULT_TIMEOUT

# Start aditional services
os.system("startx&")

# Make sure Map is hidden behind Navit Menu
os.system("xdotool mousemove 100 100 mousedown 1&")

def CarpcController_SendCommand(command):
	UDP_IP = "127.0.0.1"
	UDP_PORT = 5005

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Send request to server
	sock.sendto(command + "\0", (UDP_IP, UDP_PORT))

	sock.close()


while (not xbmc.abortRequested):

	# If Radio is Active and User is trying to play a file switch Radio OFF
	if str(xbmcgui.Window(10000).getProperty('Radio.Active')) == "true" and xbmc.Player().isPlaying():
		#xbmc.Player().stop()
		#xbmcgui.Dialog().notification('Radio', 'You are in Radio Mode', xbmcgui.NOTIFICATION_INFO, 5000)
		CarpcController_SendCommand("system_mode_toggle")
	time.sleep(5)
	
	# Display hell
	#os.system("echo 255 | sudo tee /sys/class/backlight/rpi_backlight/brightness")
	'''
	if xbmcgui.getCurrentWindowId() != 1114:
		continue
		newRawAction = xbmcgui.getMouseRawAction()

		pos = xbmcgui.getMousePosition()
		newPosX = pos/10000
		newPosY = pos%10000

		timeout = DEFAULT_TIMEOUT

		# Treat dragging actions(UP/DOWN with scroll up and scroll down)
		if newRawAction == MB_DRAG:
			# dragging is disabled
			if dragging == 0:
				dragging = 1
				posX = newPosX
				posY = newPosY
			# dragging is enabled
			else:
				if newPosY > posY:
					xbmc.executebuiltin("XBMC.Action(ScrollDown)")
					#timeout = 0.16
					timeout = ((FLICK_Y_MAX_DISTANCE - float(newPosY - posY)) * FLICK_MIN_TIMEOUT) / FLICK_Y_MAX_DISTANCE
					print "down " + str(newPosY - posY)
				elif newPosY < posY:
					xbmc.executebuiltin("XBMC.Action(ScrollUp)")
					#timeout = (float(posY - newPosY) * 0.16) / 50.0
					#timeout = 0.10
					timeout = ((FLICK_Y_MAX_DISTANCE - float(posY - newPosY)) * FLICK_MIN_TIMEOUT) / FLICK_Y_MAX_DISTANCE
					#print "up " + str(posY - newPosY)

		elif newRawAction == MB_DRAG_END:
			dragging = 0

		# Treat long click as right click
		elif newRawAction == MB_SHORT_CLICK or newRawAction == MB_LONG_CLICK:
			canHold = 1

		if canHold:
			if newRawAction == MB_NONE:
				holdCount = holdCount + 1
				#print holdCount
			if holdCount >= 20:
				#xbmc.executebuiltin("XBMC.Notification(a, b)")
				xbmc.executebuiltin("XBMC.Action(ContextMenu)")
				holdCount = 0
				canHold = 0

		if timeout < 0:
			timeout = 0
	else:
		timeout = 2
	'''