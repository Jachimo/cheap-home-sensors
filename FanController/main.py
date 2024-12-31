# FanController main.py
#  From https://github.com/Jachimo/cheap-home-sensors

import machine
import network
import asyncio

from wifimanager import WiFiManager
from mqttmanager import MQTTManager

import config

# Main
async def main():
    # Initialize classes
    wifi_manager = WiFiManager(config.WIFI_NETS)
    mqtt_manager = MQTTManager(config.MQTT_ADDR)

    try:
        if not await wifi_manager.scan_and_connect():
            print("No known networks in range, will continue to retry")
    
        wifi_t = asyncio.create_task(wifi_manager.monitor_connection())

        await asyncio.gather(wifi_t, )  # add other tasks
    
    except Exception as e:
        print("Exception - terminating")
        print(e)
        try:
            wifi_t.cancel()
            # Cancel tasks
        except (asyncio.CancelledError, NameError):
            print("Tasks cancelled")
    
    finally:
        wifi_manager.disconnect()