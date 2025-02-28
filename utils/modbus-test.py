#!/usr/bin/env python

import minimalmodbus

RETRY = 3

instrument = minimalmodbus.Instrument('/dev/serial0', 10)  # port name, slave address (in decimal)
instrument.mode = minimalmodbus.MODE_RTU
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1  # reading timeout 1 second

instrument.debug = True

# Read temperature (PV = ProcessValue)
temperature = instrument.read_register(16, 1, functioncode=4, signed=True)  # Register number, number of decimals
print(temperature)
