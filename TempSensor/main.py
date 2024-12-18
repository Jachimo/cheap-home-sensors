# Main entry point

import config  # local config.py file
import machine
import bme280_int

i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))
bme = bme280_int.BME280(i2c=i2c, address=0x76)

print(bme.values)  # human-readable, for test purposes

bme.read_compensated_data()  # returns array for further processing
