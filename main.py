#google sheets libraries
from google.oauth2 import service_account
from googleapiclient.discovery import build
#Analog input libraries
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time 
from datetime import datetime
import os
import glob
import time
import math

def main():
	temp_sensor = initialize_temp_sensor()

	#spreadsheet setup
	sheet = initialize_sheet()

	#Analog input setup
	mcp = initialize_analog_inputs()

	# create an analog input channel on pin 0
	ph_analog_input = AnalogIn(mcp, MCP.P0) #PH sensor
	tds_analog_input = AnalogIn(mcp, MCP.P1) #TDS sensor

	sensor_data = [[0,0,0,0]]
	while True:
		sensor_data[0][0]=str(datetime.now())
		sensor_data[0][1] = voltage_to_ph(ph_analog_input.voltage)
		sensor_data[0][2] = voltage_to_ppm(tds_analog_input.voltage)
		sensor_data[0][3] = read_temp()
		print(sensor_data)
		request= sheet.values().append(spreadsheetId=spreads_id, range = 'data!A1:D1', valueInputOption='USER_ENTERED', body={'values':sensor_data}).execute()
		request = sheet.values().update(spreadsheetId=spreads_id, range = 'main!A2:D2', valueInputOption='USER_ENTERED', body={'values':sensor_data}).execute()
		time.sleep(60)

def read_temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines
    
    
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    else:
        return 0.0
        
def initialize_temp_sensor():
	os.system('modprobe w1-gpio')
	os.system('modprobe w1-therm')
	 
	base_dir = '/sys/bus/w1/devices/'
	device_folder = glob.glob(base_dir + '28*')[0]
	return device_folder + '/w1_slave'

def initialize_sheet():
	SERVICE_ACCOUNT_FILE = 'felixkey.json'
	SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
	cred = None
	cred = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes = SCOPES)
	spreads_id = '1355H2Xxpo-QK8loBFWWs0eGXspbq-htX_trfQJEf1js'
	service = build('sheets', 'v4', credentials = cred)
	return service.spreadsheets()

def initialize_analog_inputs():
	# create the spi bus
	spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

	# create the cs (chip select)
	cs = digitalio.DigitalInOut(board.D5)

	# create the mcp object
	return MCP.MCP3008(spi, cs)

def voltage_to_ph(voltage):
	return -5.16*voltage+22.33

def voltage_to_ppm(voltage):
	return 76.6*math.exp(voltage*1.62)

if __name__=="__main__":
    main()
