import sys
from gattlib import GATTRequester, GATTResponse
import time
from binascii import hexlify
import socket
import logging
import os

collectFlag = False         # Indicator that the data with sequence number 0 is received
dataCollect = []            # Collected Raw data
matrix = []                 # A matrix that contains all the unintervalled data
sampleTime = []             # No more useful
ip = "185.192.112.72"       
port = 6615
currentTime = 0
frameCounter = 0            # Checking for when certain number of data frames is received
batteryInt = 2900

# This class helps us customize the GATTRequester 
class reqq(GATTRequester):
    def on_notification(self, handle, data):
        global collectFlag
        global dataCollect
        global currentTime
        global frameCounter
        data = str(hexlify(data))
        sqNumber = int(data[10:12],16)

        if (sqNumber == 0):
            collectFlag = True
            if (frameCounter == 0):
                currentTime = 	int(round(time.time() * 1000))

        if (collectFlag):
            dataCollect.append(data[8:-1])

        if (sqNumber == 251 and collectFlag == True):
            collectFlag = False
            deInterleave(dataCollect)
            dataCollect = []
            

def deInterleave(dataCollection):           
    global matrix
    global sampleTime
    global frameCounter
    global batteryInt
    final = final = [[0] * 12 for i in range(12)]
    for data in dataCollection:
        sqNumber = int(data[2] + data[3], 16)
        y = sqNumber % 12
        j = 0
        for i in range(6):
            start = 4 + 6*i
            a = int(data[start+2]+data[start:start+2], 16)
            b = int(data[start+3]+data[start+4]+data[start+5], 16)

            final[y][j] = a
            j = j + 1
            final[y][j] = b
            j = j + 1
    for k in range(12):
        for l in range(12):
            matrix.append(final[l][k])
            sampleTime.append(currentTime)

    if (frameCounter == 2):     #Change this if you want to have different number of data frames in every packet
        frameCounter = 0
        packetSend(batteryInt)
    else:
        frameCounter = frameCounter + 1





# Making the packet based on the documentation
def packetSend(batteryLevel):
    global matrix
    global sampleTime
    global currentTime
    global ip
    global port
    global infLog
    data = bytes([68, 65, 84, 65])              # ASCII code for "DATA"
    packetIDInt = int(sys.argv[3])
    packetIDstr = format(packetIDInt, '012d')
    packetIDLess = bytearray(packetIDstr, 'UTF-8')
    packetID = bytes(12-len(packetIDLess)) + packetIDLess
    auxBytes = bytes([176])
    modeBytes = bytes([255])
    sympBytes = bytes(2)
    scaleBytesInt = 1001157950
    scaleBytes = scaleBytesInt.to_bytes(4, 'little')
    batteryBytes = batteryLevel.to_bytes(2, 'little')
    timeHex = format(currentTime, '016x')
    timeBytesLess = bytearray(timeHex, 'UTF-8')
    timeBytes = bytes(16-len(timeBytesLess)) + timeBytesLess
    hrByte = bytes([1])
    counter = 0
    ecgDataBytes = matrix.pop(0).to_bytes(2, 'big')
    counter = counter + 1
    for ecgData in matrix:
        temp = ecgData.to_bytes(2, 'big')
        counter = counter + 1
        ecgDataBytes = ecgDataBytes + temp
    matrix = []
    ecgLen = 2*counter
    ecgLenBytes = ecgLen.to_bytes(2, 'big')
    xtaa = bytes([88, 84, 65, 65])          # ASCII code for "XTAA"
    oneEcgBytes = bytes([0, 2])
    tagLengthBytes = bytes([0, 0])
    noteLengthBytes = bytes([0, 0])
    crcBytes = bytes([0, 0])

    totalPacket = data + packetID + auxBytes + modeBytes + scaleBytes + batteryBytes \
                    + timeBytes + hrByte + ecgLenBytes + ecgDataBytes + xtaa + \
                        oneEcgBytes + tagLengthBytes + noteLengthBytes + crcBytes
    print("Packet sent for " + str(sys.argv[2]))
    infLog.info("Total Packet = "+str(hexlify(totalPacket)))
    try:
        s.sendall(totalPacket)
    except:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.sendall(totalPacket)
        



logCurrentTime = int(time.time())
startTime = logCurrentTime
fileName = "bDeviceError_" + str(sys.argv[1]) +"_"+str(logCurrentTime)+".log"



erLog = logging.getLogger("ERROR_LOGGER")
erLog.setLevel(logging.INFO)
eL = logging.FileHandler(fileName, mode='w')
erLog.addHandler(eL)
fileName = "bDeviceInfo_" + str(sys.argv[1]) +"_"+str(logCurrentTime)+".log"
infLog = logging.getLogger("INFO_LOGGER")
infLog.setLevel(logging.INFO)
iL = logging.FileHandler(fileName, mode='w')
infLog.addHandler(iL)


try:
    req = reqq(sys.argv[1], True, "hci0")


    battery = req.read_by_handle(0x0045)
    batteryInt = int.from_bytes(battery[0], "big")


    req.write_by_handle(0x001f, bytes([1,0]))


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))


    while True:
        time.sleep(15)

        # You cannot run read_by_handle in "on_notification" method in GATTRequester class
        battery = req.read_by_handle(0x0045)
        batteryInt = int.from_bytes(battery[0], "big")

        # We make a new log file for received data every 10 minutes 
        tempTime = int(time.time())
        if (tempTime-logCurrentTime > 600):
            logCurrentTime = tempTime
            fileName = "bDeviceInfo_" + str(sys.argv[1]) +"_"+str(logCurrentTime)+".log"
            for hdlr in infLog.handlers[:]:
                infLog.removeHandler(hdlr)
            iL = logging.FileHandler(fileName, mode='w')
            infLog.addHandler(iL)
            
except Exception as e:
    erLog.info("Start time= "+str(startTime))
    erLog.info("End Time = "+str(int(time.time())))
    erLog.info(e)


