# FanController main.py
#  From https://github.com/Jachimo/cheap-home-sensors

import machine
import network
import asyncio

from wifimanager import WiFiManager
from mqttmanager import MQTTManager

import config

# Pins

led = machine.Pin(config.led_pin, machine.Pin.OUT)
button = machine.Pin(config.button_pin, machine.Pin.IN)

relay_low = machine.Pin(config.fan_low_pin, machine.Pin.OUT)
relay_med = machine.Pin(config.fan_med_pin, machine.Pin.OUT)
relay_high = machine.Pin(config.fan_high_pin, machine.Pin.OUT)
relay_turbo = machine.Pin(config.fan_turbo_pin, machine.Pin.OUT)

# Coroutines



# Main logic
async def main():
    # Initialize classes
    wifi_manager = WiFiManager(config.WIFI_NETS)
    mqtt_manager = MQTTManager(config.MQTT_ADDR)

    try:
        if not wifi_manager.is_connected:
            await wifi_manager.scan_and_connect()
        
        if not mqtt_manager.is_connected:
            await mqtt_manager.connect()
    
    except Exception as e:
        print("Exception during startup!")
        print(e)
        await asyncio.sleep(30)  # TODO: Exponential backoff?
    
    
        
        
        
        
        
        
        
        try:
            wifi_t.cancel()
            # Cancel other tasks
        except (asyncio.CancelledError, NameError):
            print("Tasks cancelled")
    
    finally:
        wifi_manager.disconnect()

# Run with asyncio scheduling
asyncio.run(main())
