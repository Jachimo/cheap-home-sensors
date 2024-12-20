# TempSensor main.py

import machine
import config  # see config.py.sample
import network
import asyncio
import bme280_int
import collections
import ntptime



class WiFiManager:
    def __init__(self, networks):
        """
        Initialize with list of networks
        networks should be a list of tuples: [(ssid1, password1), (ssid2, password2), ...]
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
                    print("WiFi connection lost! Scanning for known networks...")
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


async def set_rtc_ntp(wifi_manager):
    while True:
        if wifi_manager.is_connected:
            ntptime.settime()  # default server is pool.ntp.org, set ntptime.host to change
            await asyncio.sleep(3600)  # update RTC hourly
        else:
            await asyncio.sleep(60)    # if network down, check again in a minute


async def read_temp():
    raw = bme.read_compensated_data()  # returns array for further processing
    tempc = raw[0] / 100  # temp in deg C
    tempf = (tempc * 1.8) + 32 
    return tempc, tempf


async def main():
    wifi_manager = WiFiManager(config.NETWORKS)
    
    try:
        if not await wifi_manager.scan_and_connect():
            print("No known networks in range, will continue to retry")

        # these will only run once connected to network
        wifi_monitor = asyncio.create_task(wifi_manager.monitor_connection())
        ntp_update = asyncio.create_task(set_rtc_ntp(wifi_manager))
        # TODO: read_temp()
        # TODO: send_mqtt_message()
        await asyncio.gather(wifi_monitor, ntp_update)  # TODO: add other tasks here
    
    except Exception as e:
        print("Exception - terminating all")
        print(e)
        try:
            wifi_monitor.cancel()
            ntp_update.cancel()
            # TODO: cancel() methods of other tasks
        except (asyncio.CancelledError, NameError):
            print("Tasks cancelled")
    
    finally:
        wifi_manager.disconnect()
    
# Run with asyncio scheduling
asyncio.run(main())
