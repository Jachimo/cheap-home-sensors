# tempsensors.py

import machine
import asyncio
import ubinascii

import bme280_int
import dht
import onewire, ds18x20

class BMESensor:
    """Class for managing Bosch BME I2C temp sensors.
    Note that BMP sensors are identical to BME but humidity == 0.
    """
    def __init__(self, scl_pin, sda_pin, i2c_address):
        i2c = machine.I2C(scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin))
        try:
            self.bme = bme280_int.BME280(i2c=i2c, address=i2c_address)
            print(f"Bosch sensor {i2c_address} initialized")
        except Exception as e:
            print(f"Failed to initialize sensor: {e}")
            raise
    
    async def read(self):
        try:
            self.rawbme = self.bme.read_compensated_data()  # returns array for further processing
            await asyncio.sleep(0.1)
            self.values = {}
            self.values['temperature_c'] = round(self.rawbme[0] / 100, 2)
            self.values['humidity'] = round(self.rawbme[1], 1)
            self.values['pressure'] = round(self.rawbme[2], 2)
            self.values['temperature'] = round((self.values['temperature_c'] * 1.8) + 32, 1)
            return self.values
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False
    
    async def read_temperature(self):
        if await self.read():
            return self.values['temperature_c'], self.values['temperature']
        else:
            return False
    
    async def read_humidity(self):
        if await self.read():
            return self.values['humidity']
        else:
            return False
    
    async def read_pressure(self):
        if await self.read():
            return self.values['pressure']
        else:
            return False


class DHT11Sensor:
    """Class for managing DHT11 temp/humid sensors."""
    def __init__(self, dht_pin):
        try:
            self.dhtsensor = dht.DHT11(machine.Pin(dht_pin))
            print(f"Initialized DHT11 on pin {dht_pin}")
        except Exception as e:
            print(f"Failed to initialize sensor: {e}")
            raise
    
    async def read(self):
        try:
            self.dhtsensor.measure()
            await asyncio.sleep(0.8)  # to allow sensor to return values
            self.values = {}
            self.values['temperature_c'] = self.dhtsensor.temperature()
            self.values['humidity'] = self.dhtsensor.humidity()
            self.values['temperature'] = round((self.values['temperature_c'] * 1.8) + 32, 2)
            return self.values
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False
    
    async def read_temperature(self):
        if await self.read():
            return self.values['temperature_c'], self.values['temperature']
        else:
            return False
    
    async def read_humidity(self):
        if await self.read():
            return self.values['humidity']
        else:
            return False


class DHT22Sensor:
    """Class for managing DHT22 temp/humid sensors."""
    def __init__(self, dht_pin):
        try:
            self.dhtsensor = dht.DHT22(machine.Pin(dht_pin))
            print(f"Initialized DHT22 on pin {dht_pin}")
        except Exception as e:
            print(f"Failed to initialize sensor: {e}")
            raise
    
    async def read(self):
        try:
            self.dhtsensor.measure()
            await asyncio.sleep(0.8)  # to allow sensor to return values
            self.values = {}
            self.values['temperature_c'] = self.dhtsensor.temperature()
            self.values['humidity'] = self.dhtsensor.humidity()
            self.values['temperature'] = round((self.values['temperature_c'] * 1.8) + 32, 2)
            return self.values
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False
    
    async def read_temperature(self):
        if await self.read():
            return self.values['temperature_c'], self.values['temperature']
        else:
            return False
    
    async def read_humidity(self):
        if await self.read():
            return self.values['humidity']
        else:
            return False

class DS18Sensor():
    def __init__(self, onewirepin):
        try:
            self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(onewirepin)))
            self.onewire_ids = self.ds_sensor.scan()
            print(f"Initialized 1-Wire sensors: {[ubinascii.hexlify(i).decode() for i in self.onewire_ids]}")
        except Exception as e:
            print(f"Failed to initialize sensor: {e}")
            raise
    
    async def read(self):
        try:
            self.ds_sensor.convert_temp()
            await asyncio.sleep(0.750)
            self.values = {}
            for id in self.onewire_ids:  # TODO: Handle multiple sensors on single 1W bus
                self.values['id'] = ubinascii.hexlify(id).decode()
                self.values['temperature_c'] = self.ds_sensor.read_temp(id)
                self.values['temperature'] = round((self.values['temperature_c'] * 1.8) + 32, 2)
            return self.values
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False
