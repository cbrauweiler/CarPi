 #!/usr/bin/env python

def maf(code): # in g/s
	try:
		#((A*256)+B) / 100
		byte1 = code.strip()[6:8]
		byte2 = code.strip()[-2:]
		return ((int(byte1,16)*256)+int(byte2,16))/100
	except:
		return code

def throttle_pos(code): #in Percent %
	try:
		code = int(code.strip()[-2:],16)
		return round(code * 100.0 / 255.0,2)
	except:
		return code

def intake_m_pres(code): # in kPa
	try:
		code = int(code.strip()[-2:],16)
		return code 
 	except:
		return code

def fuel_rate(code):
	try:
		#((A*256)+B)*0.05
		byte1 = code.strip()[6:8] 
		byte2 = code.strip()[-2:] 
		return ((int(byte1,16)*256)+int(byte2,16))*0.05
	except:
		return code
		
def rpm(code):
		try:
			#((A*256)+B)/4
			byte1 = code.strip()[6:8]
			byte2 = code.strip()[-2:] 
			return ((int(byte1,16)*256)+int(byte2,16))/4
		except:
			return code

def speed(code): # in KM/h
		try:
			return int(code.strip()[-2:],16)
		except:
			return code

def voltage(code): # in V
		try:
			#((A*256)+B)/1000
			byte1 = code.strip()[6:8]
			byte2 = code.strip()[-2:] 
			return ((int(byte1,16)*256)+int(byte2,16))/1000
		except:
			return code
			
def percent_scale(code):
	try:
		code = int(code.strip()[-2:],16)
		return round(code * 100.0 / 255.0,2)
	except:
		return code.strip()

def timing_advance(code):
		code = int(code.strip(),16)
		return (code - 128) / 2.0

def sec_to_min(code):
		try:
			byte1 = code.strip()[6:8]
			byte2 = code.strip()[-2:]
			code = byte1+byte2
			code = int(code.strip(),16)
			return round(code / 60,0)
		except:
			return code.strip()

def temp(code): #in Celsius
		try:
			return int(code.strip()[-2:],16) -40
		except:
			return code 

def cpass(code):
		#fixme
		return code

def fuel_trim_percent(code):
	try:
		#(B-128) * 100/128
		byte2 = code.strip()[-2:]
		return (int(byte2,16)-128)*100/128
	except:
		return code

		
def dtc_decrypt(code):
		num = int(code.strip()[0],16)
		if num & 1: # is mil light on
				mil = 1
		else:
				mil = 0
		# bit 0-6 are the number of dtc's. 
		num = num >> 1
		return (num, mil)

def hex_to_bitstring(str):
	 n=int(str,16)
	 return bin(n)[2:]

def mpg(speed,maf):
	return (14.7*6.17*4.54*speed)/(3600*maf/100)
	 
class Sensor:
		def __init__(self,sensorName, sensorcommand, sensorValueFunction, u):
				self.name = sensorName
				self.cmd  = sensorcommand
				self.value= sensorValueFunction
				self.unit = u

SENSORS = [
		Sensor("                                  Supported PIDs", "0100", hex_to_bitstring  ,""       ),    
		Sensor("                        Status Since DTC Cleared", "0101", dtc_decrypt       ,""       ),    
		Sensor("                        DTC Causing Freeze Frame", "0102", cpass             ,""       ),    
		Sensor("                              Fuel System Status", "0103", cpass             ,""       ),
		Sensor("                           Calculated Load Value", "0104", percent_scale     ,""       ),    
		Sensor("                             Coolant Temperature", "0105", temp              ,"C"      ),
		Sensor("                     Short Term Fuel Trim Bank 1", "0106", fuel_trim_percent ,"%"      ),
		Sensor("                      Long Term Fuel Trim Bank 1", "0107", fuel_trim_percent ,"%"      ),
		Sensor("                     Short Term Fuel Trim Bank 2", "0108", fuel_trim_percent ,"%"      ),
		Sensor("                      Long Term Fuel Trim Bank 2", "0109", fuel_trim_percent ,"%"      ),
		Sensor("                              Fuel Rail Pressure", "010A", cpass             ,""       ),
		Sensor("                        Intake Manifold Pressure", "010B", intake_m_pres     ,"kPa"    ),
		Sensor("                                      Engine RPM", "010C", rpm               ,""       ),
		Sensor("                                   Vehicle Speed", "010D", speed             ,"MPH"    ),
		Sensor("                                  Timing Advance", "010E", timing_advance    ,"degrees"),
		Sensor("                                 Intake Air Temp", "010F", temp              ,"C"      ),
		Sensor("                             Air Flow Rate (MAF)", "0110", maf               ,"lb/min" ),
		Sensor("                               Throttle Position", "0111", throttle_pos      ,"%"      ),
		Sensor("                            Secondary Air Status", "0112", cpass             ,""       ),
		Sensor("                          Location of O2 sensors", "0113", cpass             ,""       ),
		Sensor("                                O2 Sensor: 1 - 1", "0114", fuel_trim_percent ,"%"      ),
		Sensor("                                O2 Sensor: 1 - 2", "0115", fuel_trim_percent ,"%"      ),
		Sensor("                                O2 Sensor: 1 - 3", "0116", fuel_trim_percent ,"%"      ),
		Sensor("                                O2 Sensor: 1 - 4", "0117", fuel_trim_percent ,"%"      ),
		Sensor("                                O2 Sensor: 2 - 1", "0118", fuel_trim_percent ,"%"      ),
		Sensor("                                O2 Sensor: 2 - 2", "0119", fuel_trim_percent ,"%"      ),
		Sensor("                                O2 Sensor: 2 - 3", "011A", fuel_trim_percent ,"%"      ),
		Sensor("                                O2 Sensor: 2 - 4", "011B", fuel_trim_percent ,"%"      ),
		Sensor("                                 OBD Designation", "011C", cpass             ,""       ),
		Sensor("                          Location of O2 sensors", "011D", cpass             ,""       ),
		Sensor("                                Aux input status", "011E", cpass             ,""       ),
		Sensor("                         Time Since Engine Start", "011F", sec_to_min        ,"min"    ),
		Sensor("                          Engine Run with MIL on", "014E", sec_to_min        ,"min"    ),
		Sensor("Fuel Rail Pressure (relative to manifold vacuum)", "0122", cpass             ,"kPa"    ),
		Sensor("Fuel Rail Pressure (diesel, gasoline direct inj)", "0123", cpass             ,"kPa(gau"),
		Sensor("                                Fuel Level Input", "012F", percent_scale     ,"%"      ),
		Sensor("                         Ambient air temperature", "0146", temp              ,"C"      ),
		Sensor("             Relative accelerator pedal position", "015A", percent_scale     ,"C"      ),
		Sensor("                                Engine fuel rate", "015E", fuel_rate         ,"l/hr"   ),
		Sensor("                          Control module voltage", "0142", voltage           ,"V"   ),
		]
		 
		
#___________________________________________________________

def test():
		for i in SENSORS:
				print i.name, i.value("F")

if __name__ == "__main__":
		test()
