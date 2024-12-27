# tempsensors.py

import machine
import bme280_int
import dht
import asyncio

class BMESensor:
    """Class for managing Bosch BME I2C temp sensors.
    Note that BMP sensors are identical to BME but humidity == 0.
    """
    def __init__(self, scl_pin, sda_pin, i2c_address):
        i2c = machine.I2C(scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin))
        try:
            self.bme = bme280_int.BME280(i2c=i2c, address=i2c_address)
            print("BME280 sensor initialized")
        except Exception as e:
            print(f"Failed to initialize sensor: {e}")
            raise
    
    async def read(self):
        try:
            self.rawbme = self.bme.read_compensated_data()  # returns array for further processing
            await asyncio.sleep(0.1)
            self.tempc = round(self.rawbme[0] / 100, 1)
            self.humid = round(self.rawbme[1], 1)
            self.press = round(self.rawbme[2], 2)
            self.tempf = round((self.tempc * 1.8) + 32, 1)
            return True
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False
    
    async def read_temperature(self):
        await self.read()
        return self.tempc, self.tempf
    
    async def read_humidity(self):
        await self.read()
        return self.humid
    
    async def read_pressure(self):
        await self.read()
        return self.press


class DHT11Sensor:
    """Class for managing DHT11 temp/humid sensors."""
    def __init__(self, dht_pin):
        self.dht = dht.DHT11(machine.Pin(dht_pin))
    
    async def read(self):
        try:
            self.dht.measure()
            await asyncio.sleep(0.8)  # to allow sensor to return values
            self.tempc = self.dht.temperature()
            self.humid = self.dht.humidity()
            self.tempf = round((self.tempc * 1.8) + 32, 1)
            return True
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False
    
    async def read_temperature(self):
        await self.read()
        return self.tempc, self.tempf
    
    async def read_humidity(self):
        await self.read()
        return self.humid


class DHT22Sensor:
    """Class for managing DHT22 temp/humid sensors."""
    def __init__(self, dht_pin):
        self.dhtsensor = dht.DHT22(machine.Pin(dht_pin))
        print(f"Initialized DHT22 on pin {dht_pin}")
    
    async def read(self):
        try:
            self.dhtsensor.measure()
            await asyncio.sleep(0.7)  # to allow sensor to return values
            self.tempc = self.dhtsensor.temperature()
            self.humid = self.dhtsensor.humidity()
            self.tempf = round((self.tempc * 1.8) + 32, 1)
            return True
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False
        
    async def read_temperature(self):
        if await self.read():
            return self.tempc, self.tempf
        else:
            print(f"Error in read_temperature()")
            return False
    
    async def read_humidity(self):
        if await self.read():
            return self.humid
        else:
            print(f"Error in read_humidity()")
            return False
