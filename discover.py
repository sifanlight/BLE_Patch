# import sys
from gattlib import DiscoveryService
import os
import subprocess
import time
import threading
import logging


os.system("sudo pkill -f notif.py")		#Ensures no subprocceses are running

counter = 1				# This counter gives unique name to each device. (For example Device 3)
addressList = []		# LIst of all connected devices
deviceList = []			# List of the names of the devices
p = []					# We keep proccesses that are running with their name and address in this list
idDict = {}				# A dictionary that assigns every 
idCounter = 0			

def inputDaemon():					# This input Daemon work on a different thread 
	while True:
		x = ""
		while (x != 'q'):
			x =  input("Press q to exit")
			if (x == 'q'):
				for proc in p:
					proc[0].terminate()
				os._exit(1)


def getPacketID(address):			# Waiting for API
	global idCounter
	global idDict
	pList = [928158855975, 662650356902, 949953139870]
	if address not in idDict:
		idDict[address] = pList[idCounter]
		idCounter = idCounter + 1



# Creating Log file
logCurrentTime = int(time.time())
fileName = "mainHub_" + str(logCurrentTime)+".log"
logger = logging.getLogger("")
logger.setLevel(logging.INFO)
lgHnd = logging.FileHandler(fileName, mode = 'w')
logger.addHandler(lgHnd)





try:
	# First Scan
	service = DiscoveryService("hci0")
	devices = service.discover(2)
	for address, name in devices.items():
		if (name == "ECG_PATCH"):
			addressList.append(address)
			deviceList.append("device"+str(counter))
		counter = counter + 1
	dCounter = 0
	for a in addressList:
		getPacketID(a)
		packetIDAddress = idDict[a]
		p.append([subprocess.Popen(["python3", "notif.py", str(a), deviceList[dCounter], str(packetIDAddress)]), a, deviceList[dCounter]])	# Running the subprocess for each address
		logger.info("Time = " + str(int(time.time())))
		logger.info("Device with address " + str(a) +" Connected as "+deviceList[dCounter])
		print("Device with address " + str(a) +" Connected as "+deviceList[dCounter])
		dCounter = dCounter + 1


	# Running input daemon
	inpD = threading.Thread(target=inputDaemon)
	inpD.daemon = True
	inpD.start()

	while True:
		time.sleep(10)


		# Checking if any of the processes has stopped running 
		indexList = []
		for  i, proc in enumerate(p):
			poll = proc[0].poll()
			if poll is not None:
				logger.info("Time = " + str(int(time.time())))
				logger.info(proc[2] + " is disconnected")
				print(proc[2] + " is disconnected")
				proc[0].terminate()
				addressList.remove(proc[1])
				indexList.append(i)
		print(indexList)
		indexList.sort(reverse=True)
		for i in indexList:
			p.pop(i)
		for proc in p:
			print(proc)


		time.sleep(5)				


		# Scanning for new devices
		service = DiscoveryService("hci0")
		devices = service.discover(1)
		for address, name in devices.items():
			if (name == "ECG_PATCH"):
				if (address not in addressList) :
					getPacketID(address)
					packetIDAddress = idDict[address]
					addressList.append(address)
					deviceList.append("device"+str(counter))
					counter = counter + 1
					p.append([subprocess.Popen(["python3", "notif.py", str(address), deviceList[dCounter], str(packetIDAddress)]), address, deviceList[dCounter]])
					logger.info("Time = " + str(int(time.time())))
					logger.info("Device with address " + str(address) +" Connected as "+deviceList[dCounter])
					print("Device with address " + str(address) +" Connected as "+deviceList[dCounter])
					dCounter = dCounter + 1
		
except Exception as e:
	print(e)
	logger.info("Time = " + str(int(time.time())))
	logger.info(e)
	for proc in p:
		proc[0].terminate()
			

