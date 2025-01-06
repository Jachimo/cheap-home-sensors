# FanController main.py
#  From https://github.com/Jachimo/cheap-home-sensors

import machine
import network
import asyncio
import gc
import time

from wifimanager import WiFiManager
from mqttmanager import MQTTManager
from fancontroller import Fan

import config

MQTT_TOPIC = f"{config.MQTT_TOPIC_BASE}/{config.MQTT_TOPIC_ID}"
MQTT_KEEPALIVE = 10  # keepalive interval in seconds

async def loop(wifi_manager, mqtt_manager):  # main loop
    while True:
        if not mqtt_manager.is_connected:  # This could be moved into mqttmanager.py as monitor_connection()
            # TODO: Set LWT message before connect...
            if mqtt_manager.connect():
                print("Connected to MQTT broker")
                mqtt_lastcontact = round(time.time())
                # TODO: ...and set 'connected' message immediately after.
            else:
                print("Waiting 30 seconds before re-attempting")
                gc.collect()
                await asyncio.sleep(30)
                continue
        if (time.time() - mqtt_lastcontact) >= MQTT_KEEPALIVE:
            print("MQTT keepalive timer expired")
            if mqtt_manager.keepalive():
                print("Keepalive successful")
                mqtt_lastcontact = round(time.time())
            else:
                # if keepalive fails for some reason...
                print("Problem while performing MQTT keepalive")
                gc.collect()
                await asyncio.sleep(10)
                continue
        
        # first, set callback for incoming MQTT messages
        # then, subscribe to desired control topic

        await asyncio.sleep(1)  # loop interval

async def main():
    # Initialize classes
    wifi_manager = WiFiManager(config.WIFI_NETS)
    mqtt_manager = MQTTManager(config.MQTT_ADDR)
    fan = Fan(config.RELAYS)  # see config.py for GPIO assignments

    try:
        if not await wifi_manager.scan_and_connect():
            print("No known networks in range, will continue to retry")
    
        wifi_t = asyncio.create_task(wifi_manager.monitor_connection())
        loop_t = asyncio.create_task(loop(wifi_manager, mqtt_manager))

        await asyncio.gather(wifi_t, loop_t)
    
    except Exception as e:
        print("Exception during startup!")
        print(e)
        try:
            wifi_t.cancel()
            # Cancel other tasks
        except (asyncio.CancelledError, NameError):
            print("Tasks cancelled")
    
    finally:
        wifi_manager.disconnect()

# Run with asyncio scheduling
asyncio.run(main())
