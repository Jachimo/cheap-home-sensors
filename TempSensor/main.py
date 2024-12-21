# TempSensor main.py

import machine
import config  # see config.py.sample
import network
import asyncio
import bme280_int
import collections
import ntptime
import time



# Utility Classes

class WiFiManager:
    def __init__(self, networks):
        """
        Initialize with list of networks.
        Networks should be a list of tuples: [(ssid1, password1), (ssid2, password2), ...]
        """
        self.networks = networks
        self.wlan = network.WLAN(network.STA_IF)
        self.is_connected = False
        self.current_network = None
    
    async def try_connect(self, ssid, password, timeout=10):
        """Attempt to connect to a specific network"""
        print(f'Attempting to connect to "{ssid}"...')
        self.wlan.connect(ssid, password)
        
        start_time = time.time()
        while not self.wlan.isconnected():
            if time.time() - start_time > timeout:
                return False
            await asyncio.sleep(0.1)
        
        return True

    async def scan_and_connect(self, timeout=10):
        """Scan for available networks and try to connect to known ones"""
        if not self.wlan.active():
            self.wlan.active(True)
        
        # Scan for available networks
        print("Scanning for networks...")
        available_networks = set(ssid.decode() for ssid, *_ in self.wlan.scan())
        # Note: We could retain RSSI info and choose strongest known network, if needed
        
        # Try each known network that is in range
        for ssid, password in self.networks:
            if ssid in available_networks:
                print(f'Found known network "{ssid}"')
                try:
                    if await self.try_connect(ssid, password, timeout):
                        self.is_connected = True
                        self.current_network = ssid
                        print(f'Successfully connected to "{ssid}"')
                        print(f'Network config: {self.wlan.ifconfig()}')
                        return True
                except Exception as e:
                    print(f'Failed to connect to "{ssid}": {e}')
        
        print("Could not connect to any known network")
        return False

    async def monitor_connection(self):
        """Monitor WiFi connection and reconnect if necessary"""
        while True:
            if not self.wlan.isconnected():
                if self.is_connected:  # Only print if we're losing an existing connection
                    print("WiFi connection lost - Rescanning")
                self.is_connected = False
                try:
                    await self.scan_and_connect()
                except Exception as e:
                    print(f"Reconnection failed: {e}")
            await asyncio.sleep(5)
    
    def disconnect(self):
        """Disconnect from WiFi"""
        if self.wlan.active():
            self.wlan.active(False)
            self.is_connected = False
            self.current_network = None
            print("WiFi disabled")


class SensorManager:
    def __init__(self, scl_pin, sda_pin):
        i2c = machine.I2C(scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin))
        try:
            self.bme = bme280_int.BME280(i2c=i2c, address=0x76)
            print("BME280 sensor initialized")
        except Exception as e:
            print(f"Failed to initialize BME280: {e}")
            raise
    
    def read_temperature(self):
        try:
            self.rawbme = self.bme.read_compensated_data()  # returns array for further processing
            self.tempc = self.rawbme[0] / 100  # temp in deg C
            self.tempf = (self.tempc * 1.8) + 32 
            return self.tempc, self.tempf
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return None


# Timer-Driven Functions

async def set_rtc_ntp(wifi_manager):
    while True:
        if wifi_manager.is_connected:
            ntptime.settime()  # default server is pool.ntp.org, set ntptime.host to change
            await asyncio.sleep(3600)  # update RTC hourly
        else:
            await asyncio.sleep(60)    # if network down, check again in a minute


async def check_sensor(sensor_manager):
    while True:
        temps = sensor_manager.read_temperature()
        if temps is not None:
            print("Temperature is ", temps)
            await asyncio.sleep(30)
        else:
            print("Failed to read temperature")
            await asyncio.sleep(10)


# Main Loop

async def main():
    # Initialize the "managers"
    wifi_manager = WiFiManager(config.WIFI_NETS)
    sensor_manager = SensorManager(scl_pin=5, sda_pin=4)  # Change as needed based on hardware

    try:
        if not await wifi_manager.scan_and_connect():
            print("No known networks in range, will continue to retry")

        wifi_t = asyncio.create_task(wifi_manager.monitor_connection())
        ntp_t = asyncio.create_task(set_rtc_ntp(wifi_manager))
        temp_t = asyncio.create_task(check_sensor(sensor_manager))
        # mqtt_t = asyncio.create_task(mqtt_transmit(???))

        await asyncio.gather(wifi_t, ntp_t, temp_t)  # ,mqtt_t)
    
    except Exception as e:
        print("Exception - terminating")
        print(e)
        try:
            wifi_t.cancel()
            ntp_t.cancel()
            temp_t.cancel()
            # mqtt_t.cancel()
        except (asyncio.CancelledError, NameError):
            print("Tasks cancelled")
    
    finally:
        wifi_manager.disconnect()
    
# Run with asyncio scheduling
asyncio.run(main())
