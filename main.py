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

#spreadsheet setup
SERVICE_ACCOUNT_FILE = 'felixkey.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
cred = None
cred = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes = SCOPES)
spreads_id = '1355H2Xxpo-QK8loBFWWs0eGXspbq-htX_trfQJEf1js'
service = build('sheets', 'v4', credentials = cred)
sheet =service.spreadsheets()

arr = [[0,0,0,0]]
#Analog input setup
# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)
chan1 = AnalogIn(mcp, MCP.P1)
chan2 = AnalogIn(mcp, MCP.P2)
#chan3 = AnalogIn(mcp, MCP.P3)

while True:
	arr[0][0]=str(datetime.now())
	arr[0][1] = chan.voltage
	arr[0][2] = chan1.voltage
	arr[0][3] = chan2.voltage
	print(arr)
	request= sheet.values().append(spreadsheetId=spreads_id, range = 'data!A1:D1', valueInputOption='USER_ENTERED', body={'values':arr}).execute()
	request = sheet.values().update(spreadsheetId=spreads_id, range = 'main!A2:D2', valueInputOption='USER_ENTERED', body={'values':arr}).execute()
	time.sleep(60)
