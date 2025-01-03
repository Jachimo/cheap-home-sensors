# TempSensor main.py - https://github.com/Jachimo/cheap-home-sensors
#  Note: asyncio support is required!
#
# Development version 20250103T1428
# This version customized for a single DS18 probe sender unit

import machine
import network
import asyncio
import collections
import ntptime
import time
import gc

from wifimanager import WiFiManager
from mqttmanager import MQTTManager

#from tempsensors import BMESensor
#from tempsensors import DHT22Sensor
from tempsensors import DS18Sensor

import config  # see config.py.sample


# Timer-Driven Coroutines

async def set_rtc_ntp(wifi_manager):
    ntptime.host = "pool.ntp.org"
    while True:
        gc.collect()
        if wifi_manager.is_connected:
            ntptime.settime()
            print(f"RTC successfully set via NTP from {ntptime.host}")
            await asyncio.sleep(3600)  # update RTC hourly
        else:
            print(f"RTC clock set failed (tried {ntptime.host}")
            await asyncio.sleep(60)    # if network down, check again in a minute


async def acquire_transmit(wifi_manager, sensor, mqtt_manager, topic_base="sensor"):
    while True:
        gc.collect()
        if wifi_manager.is_connected:
            if not mqtt_manager.is_connected:
                await mqtt_manager.connect()
            if mqtt_manager.is_connected:
                try:
                    svalues = await sensor.read()
                except Exception as e:
                    print("Exception while reading sensor")
                    print(e)
                    await asyncio.sleep(2)
                    try:
                        sensor.reset()
                        continue
                    except Exception as e:
                        print("Exception while attempting to reset sensor")
                        print(e)
                        raise
                
                if 'id' in svalues:
                    # If the sensor has its own ID, use it
                    pub_id = svalues['id'][-8:]
                else:
                    # But if not, publish directly under the tx unit ID
                    pub_id = config.SENSOR_ID
                
                if config.DEBUG:
                    svalues['free_memory'] = gc.mem_free()
                
                for key, value in svalues.items():
                    mqtt_manager.publish(f"{topic_base}/{pub_id}/{key}", str(value))
                    print(f"{topic_base}/{pub_id}/{key} =", str(value))
                await asyncio.sleep(30)  # Sensor reading interval
            else:
                await asyncio.sleep(5)  # Wait for MQTT
        else:
            await asyncio.sleep(5)  # Wait for WiFi


# Main Loop

async def main():
    print(f"Starting up unit {config.SENSOR_ID}")
    wifi_manager = WiFiManager(config.WIFI_NETS)
    mqtt_manager = MQTTManager(config.MQTT_ADDR)
    
    #sensor_bme = BMESensor(scl_pin=5, sda_pin=4, i2c_address=0x76)
    #sensor_dht = DHT22Sensor(13)  # GPIO 13 is D7 on the WeMos D1
    sensor_ds  = DS18Sensor(14)    # GPIO 14 is D5 on the WeMos D1

    try:
        if not await wifi_manager.scan_and_connect():
            print("No known networks in range, will continue to retry")
            
        wifi_t = asyncio.create_task(wifi_manager.monitor_connection())
        ntp_t = asyncio.create_task(set_rtc_ntp(wifi_manager))
        
        # TODO: Send tx unit's IP address to MQTT server 
        
        #bme_t = asyncio.create_task(acquire_transmit(wifi_manager, sensor_bme, mqtt_manager))
        #dht_t = asyncio.create_task(acquire_transmit(wifi_manager, sensor_dht, mqtt_manager))
        ds_t  = asyncio.create_task(acquire_transmit(wifi_manager, sensor_ds, mqtt_manager))
        
        await asyncio.gather(wifi_t, ntp_t, ds_t)

    except (Exception, KeyboardInterrupt) as e:
        print("STOP: Terminating and resetting")
        print(e)
        try:
            ntp_t.cancel()
            #dht_t.cancel()
            ds_t.cancel()
            #bme_t.cancel()
            wifi_t.cancel()
        except (asyncio.CancelledError, NameError):
            print("Tasks cancelled")
    
    finally:
        mqtt_manager.disconnect()
        wifi_manager.disconnect()
        
        print("System resetting!")
        machine.reset()
    
# Run with asyncio scheduling
asyncio.run(main())
