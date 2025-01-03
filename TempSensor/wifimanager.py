# WiFi Manager Class
#  From https://github.com/Jachimo/cheap-home-sensors

import asyncio
import network
import time

import config

class WiFiManager:
    def __init__(self, networks):
        """
        Initialize with list of networks.
        Networks should be a list of tuples: [(ssid1, password1), (ssid2, password2), ...]
        """
        self.networks = networks
        self.hostname = config.SENSOR_ID
        self.wlan = network.WLAN(network.STA_IF)
        self.is_connected = False
        self.current_network = None
    
    async def try_connect(self, ssid, password, timeout=10):
        """Attempt to connect to a specific network"""
        print(f'Attempting to connect to "{ssid}"...')
        
        network.hostname(self.hostname)  # sets DHCP Client ID
        self.wlan.connect(ssid, password)
        
        start_time = time.time()
        while not self.wlan.isconnected():
            if time.time() - start_time > timeout:
                return False
            await asyncio.sleep(0.5)
        
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
                        print(f'Network config: {self.wlan.ifconfig()}')  # tuple (ipaddress, subnet mask, gateway, DHCP)
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
