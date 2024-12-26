# tempsensors.py

import machine
import bme280_int
import dht

class BMESensor:
    """Class for managing Bosch I2C temp sensors."""
    def __init__(self, scl_pin, sda_pin, i2c_address):
        i2c = machine.I2C(scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin))
        try:
            self.bme = bme280_int.BME280(i2c=i2c, address=i2c_address)
            print("BME280 sensor initialized")
        except Exception as e:
            print(f"Failed to initialize sensor: {e}")
            raise
    
    def read_temperature(self):
        try:
            self.rawbme = self.bme.read_compensated_data()  # returns array for further processing
            self.tempc = self.rawbme[0] / 100  # temp in deg C
            self.tempf = round((self.tempc * 1.8) + 32, 1)
            return self.tempc, self.tempf
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return None

class DHT11Sensor:
    """Class for managing DHT temp/humid sensors."""
    def __init__(self, dht_pin):
        self.dht = dht.DHT11(machine.Pin(dht_pin))
    
    async def read_temperature(self):
        try:
            await asyncio.sleep(2)  # may not be necessary
            self.dht.measure()
            self.tempc = self.dht.temperature()
            self.humid = self.dht.humidity()
            self.tempf = round((self.tempc * 1.8) + 32, 1)
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return None
