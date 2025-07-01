# tempsensors.py by @Jachimo
#  From https://github.com/Jachimo/cheap-home-sensors

from abc import ABC, abstractmethod
from typing import Union

import machine
import asyncio
import ubinascii
import dht
import onewire, ds18x20

import bme280_int


class TempSensor(ABC):
    """
    Base class for various types of temperature sensors.
    """
    def __init__(self) -> None:
        self.values: dict = {}
        self.sensor_type: str = ""

    @abstractmethod
    async def read(self) -> Union[dict, bool]:  # should populate and return self.values OR False if reading fails
        pass

    @abstractmethod
    async def reset(self) -> None:  # set up the connection to the sensor; should be idempotent
        pass

    async def read_temperature(self) -> Union[tuple, bool]:
        """ Read sensor, return the temp in C and F. """
        if await self.read():
            return self.values['temperature_c'], self.values['temperature']
        else:
            return False
    
    async def read_humidity(self) -> Union[float, bool]:
        """ Read sensor, return only the RH in percent """
        if await self.read():
            return self.values['humidity']
        else:
            return False
    
    async def read_pressure(self) -> Union[float, bool]:
        """ Read sensor, return only the barometric pressure in Pa """
        if await self.read():
            return self.values['pressure']
        else:
            return False


class BMESensor(TempSensor):
    """
    Class for managing Bosch BME I2C temp sensors.
    Also works for Bosch BMP sensors, but they always report humidity == 0.
    """
    def __init__(self, scl_pin: int, sda_pin: int, i2c_address: int) -> None:
        self.sensor_type: str = "BME"
        self.scl: int = scl_pin
        self.sda: int = sda_pin
        self.i2c_addr: int = i2c_address
        self.reset()
    
    def reset(self) -> None:
        i2c = machine.I2C(scl=machine.Pin(self.scl), sda=machine.Pin(self.sda))
        try:
            self.bme = bme280_int.BME280(i2c=i2c, address=self.i2c_addr)
            print(f"Bosch sensor {self.i2c_addr} initialized")
        except Exception as e:
            print("Failed to reset BME sensor")
            print(e)
            raise
    
    async def read(self) -> Union[dict, bool]:
        """ Read sensor, create and return a dict of the temp (in F and C), pressure, and RH """
        try:
            self.rawbme = self.bme.read_compensated_data()  # returns an array
            await asyncio.sleep(0.5)
            self.values['temperature_c'] = round(self.rawbme[0] / 100, 2) # bme280_int returns (Tc * 100) 
            self.values['pressure'] = round(self.rawbme[1] / 256)  # sensor returns units of Pa * 256
            self.values['humidity'] = round(self.rawbme[2], 1)  # BMP sensor will always report 0
            self.values['temperature'] = round((self.values['temperature_c'] * 1.8) + 32, 1)  # sensor reports in C so convert to F
            return self.values
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False


class DHT11Sensor(TempSensor):
    """ Class for managing DHT11 temp/humid sensors. """
    def __init__(self, dht_pin: int) -> None:
        self.sensor_type: str = "DHT11"
        self.sensor_pin: int = dht_pin
        self.reset()
    
    def reset(self) -> None:
        try:
            self.dht = dht.DHT11(machine.Pin(self.sensor_pin))
            print(f"Initialized DHT11 on pin {self.sensor_pin}")
        except Exception as e:
            print(f"Failed to reset sensor: {e}")
            raise
    
    async def read(self) -> Union[dict, bool]:
        try:
            self.dht.measure()
            await asyncio.sleep(0.8)  # 800ms to allow sensor to return values
            self.values['temperature_c'] = self.dht.temperature()
            self.values['humidity'] = self.dht.humidity()
            self.values['temperature'] = round((self.values['temperature_c'] * 1.8) + 32, 2)
            return self.values
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False


class DHT22Sensor(TempSensor):
    """ Class for managing DHT22 temp/humid sensors. """
    def __init__(self, dht_pin: int) -> None:
        self.sensor_type: str = "DHT22"
        self.sensor_pin: int = dht_pin
        self.reset()
    
    def reset(self) -> None:
        try:
            self.dhtsensor = dht.DHT22(machine.Pin(self.sensor_pin))
            print(f"Reinitialized DHT22 on pin {self.sensor_pin}")
        except Exception as e:
            print(f"Failed to reset sensor: {e}")
            raise
    
    async def read(self) -> Union[dict, bool]:
        try:
            self.dhtsensor.measure()
            await asyncio.sleep(0.8)  # to allow sensor to return values, reportedly sometimes slow
            self.values['temperature_c'] = float(self.dhtsensor.temperature())
            self.values['humidity'] = float(self.dhtsensor.humidity())
            self.values['temperature'] = round((self.values['temperature_c'] * 1.8) + 32, 2)
            return self.values
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False


class DS18Sensor(TempSensor):
    """ Class for managing DS18x20 (or clones) connected via OneWire interface bus. """
    def __init__(self, onewire_pin: int) -> None:
        self.sensor_type: str = "DS18"
        self.sensor_pin: int = onewire_pin
        self.reset()
    
    def reset(self) -> None:
        try:
            self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(self.sensor_pin)))
            self.onewire_ids = self.ds_sensor.scan()  # possible to have multiple sensors on same line
            print(f"Reinitialized 1-Wire sensors: {[ubinascii.hexlify(i).decode() for i in self.onewire_ids]}")
        except Exception as e:
            print("Failed to reset DS18 sensor")
            print(e)
            raise
    
    async def read(self) -> Union[dict, bool]:
        try:
            self.ds_sensor.convert_temp()  # tell sensor to read, and get values from sensor
            await asyncio.sleep(0.750)  # wait for values - could probably be faster than 750ms
            for id in self.onewire_ids:  # TODO: Test case of multiple OneWire sensors on some pin
                self.values['id'] = ubinascii.hexlify(id).decode()
                self.values['temperature_c'] = float(self.ds_sensor.read_temp(id))
                self.values['temperature'] = round((self.values['temperature_c'] * 1.8) + 32, 2)
            return self.values
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return False
