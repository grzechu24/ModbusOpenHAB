#!/usr/bin/env python

import sys
import minimalmodbus


# Arguments
if len(sys.argv) < 4:
    print("ARGS: address, register, value, [number of decimals]")
    sys.exit(1)
slave_addr = int(sys.argv[1])
reg_num = int(sys.argv[2])
write_value = int(sys.argv[3])
num_decimal = int(sys.argv[4]) if len(sys.argv) > 4 else 0

instrument = minimalmodbus.Instrument('/dev/serial0', slave_addr)  # port name, slave address (in decimal)
instrument.mode = minimalmodbus.MODE_RTU
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1  # reading timeout 1 second
# instrument.debug = True

# Read temperature (PV = ProcessValue)
instrument.write_register(reg_num, write_value, number_of_decimals=num_decimal)
