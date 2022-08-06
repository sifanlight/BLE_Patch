## Patch Handler
This version has the following features:
* Scan and connected to devices with the name "ECG_PATCH"
* Connected to multiple devices ( Tested with 3 ECG Patches)
* log of all sent packets and errors
* Gives each bluetooth device a unique PacketID. If the device is disconneted and reconnect again, the same PacketID will be given to that device
* Sends ECG data and battery data for each device to server
* A ready to use input daemon for custom commands

As for now, the packetID codes are pre determined and we are waiting for an API to get PacketID based on the device's bluetooth address.
## Requirement 
This code has been tested on python 3.8 and 3.10 but it should be able to run on python 3.4 and above. This code requires gattlib python library. </br>
To install gattlib library first install these packages:
```
sudo apt install pkg-config libboost-python-dev libboost-thread-dev libbluetooth-dev libglib2.0-dev
```
And then run:
```
pip3 install gattlib
```
## Usage

Please do not change the name of the file ```notif.py``` as it will break the program.</br>
If you use any other bluetooth device other than ```hci0``` please make these changes in both of the files:

discover.py:
```

try:
	# First Scan
	service = DiscoveryService("hci0")
	devices = service.discover(2)
	for address, name in devices.items():
		if (name == "ECG_PATCH"):
			addressList.append(address)
			deviceList.append("device"+str(counter))
		counter = counter + 1
        ...
.
.
.
.
.

# Scanning for new devices
		service = DiscoveryService("hci0")
		devices = service.discover(1)
		for address, name in devices.items():
			if (name == "ECG_PATCH"):
				if (address not in addressList) :
					getPacketID(address)
					packetIDAddress = idDict[address]
					...
		
```
notif.py
```
req = reqq(sys.argv[1], True, "hci0")
```
To use this program run discover.py with root permission:
```
sudo python3 discover.py
```

You can also run the notification receiver for just one device with this syntax:
```
sudo python3 notif.py <Address> <Name for Device> <PacketID>
```