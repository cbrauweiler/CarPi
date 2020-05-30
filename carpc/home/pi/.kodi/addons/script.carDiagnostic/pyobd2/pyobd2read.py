#!/usr/bin/python
import curses
import obd_io
from powertrain_codes import pcodes
import threading
import Queue
import re
from optparse import OptionParser

class OBDGui:
 def __init__(self,screen,options):
  self.screen = screen 
  curses.halfdelay(10)
  self.infolines=['no port open']
  self.mode='main'
  self.options=options

 def drawFrame(self):
  self.screen.clear()
  if self.mode=='main':self.infostr='q: quit, o: open port'
  elif self.mode=='open':self.infostr='q: quit, r: read code, c: clear code, s: read sensors'
  elif self.mode=='sensor':self.infostr='q: quit, b: back'
  self.screen.addstr(0,0,self.infostr)
  i=0
  for ln in self.infolines:
   self.screen.addstr(2+i,0,ln)
   i+=1
  self.screen.refresh()

 def showSensors(self):
  def cmpS(a,b):
   ai=int(re.findall('\d+',a)[0])
   bi=int(re.findall('\d+',b)[0])
   return cmp(ai,bi)
  if not self.sensorReader.queue_done.empty():
   sensor_names = self.port.sensor_names()
   while not self.sensorReader.queue_done.empty():
     sensor=self.sensorReader.queue_done.get()
     s = str(sensor.id)+'\t'+sensor.value[0]
     self.sensorresults[str(sensor.id)]=s+':'+str(sensor.value[1])+' '+sensor.value[2]
   self.infolines=[]
   for result in self.sensorresults:
     self.infolines.append(self.sensorresults[result]) 
   self.infolines.sort(cmpS)  #This needs to be fixed

 def openport(self):
  try:
   self.port=obd_io.OBDPort(self.options.port)
   self.sensorReader=obd_io.sensorReader(self.port)
   self.sensorReader.start()
   self.sensorReader.refresh()
   self.sensorresults={}
   self.infolines=['port opened']
  except Exception as e:
   raise(e) 
   self.infolines=['port open failed ...']

 def readDTC(self):
  adtc=self.port.get_dtc()
  codearr=obd_io.decrypt_dtc_code(adtc)
  if len(codearr)>0:
   self.infolines=[codearr[0]+' : '+pcodes[codearr[0]]]
  else:
   self.infolines=['no code to read']

 def clearDTC(self):
  self.port.clear_dtc()
  self.infolines=['DTC code erased']

 def run(self):
  while True:
   self.drawFrame()
   c=self.screen.getch()
   if self.mode=='main':
    if c==ord('q'):break
    elif c==ord('o'): 
     self.openport()
     self.mode='open'
     continue
   elif self.mode=='open':
    if c==ord('r'):self.readDTC() 
    elif c==ord('c'):self.clearDTC()
    elif c==ord('s'):
     self.infolines=['reading sensors..']
     self.mode='sensor' 
     continue
    elif c==ord('q'):break
   elif self.mode=='sensor':
    self.showSensors()
    if c==ord('q'):break
    elif c==ord('b'):self.mode='open'
    if self.sensorReader.queue.empty():self.sensorReader.refresh()

def main(screen):
    a=OBDGui(screen,options)
    a.run()
  
if __name__=='__main__':
    parser=OptionParser();
    parser.add_option("-p", "--port", dest="port", default="COM12",help="port , such as /dev/ttyACM0")
    (options, args) = parser.parse_args()    
    curses.wrapper(main)
