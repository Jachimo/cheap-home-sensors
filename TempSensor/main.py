# TempSensor main.py
#  From https://github.com/Jachimo/cheap-home-sensors

import machine
import network
import asyncio
import collections
import ntptime
import time

from wifimanager import WiFiManager
#from tempsensors import BMESensor
from tempsensors import DHT22Sensor
from mqttmanager import MQTTManager

import config  # see config.py.sample


# Timer-Driven Coroutines

async def set_rtc_ntp(wifi_manager):
    ntptime.host = "pool.ntp.org"
    while True:
        if wifi_manager.is_connected:
            ntptime.settime()
            print(f"RTC successfully set via NTP from {ntptime.host}")
            await asyncio.sleep(3600)  # update RTC hourly
        else:
            print(f"RTC clock set failed (tried {ntptime.host}")
            await asyncio.sleep(60)    # if network down, check again in a minute


async def acquire_transmit(wifi_manager, sensor, mqtt_manager, topic_base="sensor"):
    while True:
        if wifi_manager.is_connected:
            if not mqtt_manager.is_connected:
                await mqtt_manager.connect()
            if mqtt_manager.is_connected:
                temps = sensor.read_temperature()
                if temps is not None:
                    temp_c, temp_f = temps
                    mqtt_manager.publish(f"{topic_base}/{config.SENSOR_ID}/temperature", str(temp_f))
                    print(f"{topic_base}/{config.SENSOR_ID}/temperature =", str(temp_f))
                await asyncio.sleep(30)  # Sensor reading interval
            else:
                await asyncio.sleep(5)  # Wait before retry
        else:
            await asyncio.sleep(5)  # Wait for WiFi


# Main Loop

async def main():
    # Initialize classes
    wifi_manager = WiFiManager(config.WIFI_NETS)
    mqtt_manager = MQTTManager(config.MQTT_ADDR)
    #sensor_bme = BMESensor(scl_pin=5, sda_pin=4, i2c_address=0x76)
    sensor_dht = DHT22Sensor(dht_pin=13)  # GPIO 13 (Pin 13) is D7 on the Wemos D1

    try:
        if not await wifi_manager.scan_and_connect():
            print("No known networks in range, will continue to retry")
            
        wifi_t = asyncio.create_task(wifi_manager.monitor_connection())
        ntp_t = asyncio.create_task(set_rtc_ntp(wifi_manager))
        mqtt_t = asyncio.create_task(
            acquire_transmit(wifi_manager, sensor_bme, mqtt_manager)
        )
        
        await asyncio.gather(wifi_t, ntp_t, mqtt_t)

    except Exception as e:
        print("Exception - terminating")
        print(e)
        try:
            wifi_t.cancel()
            ntp_t.cancel()
            mqtt_t.cancel()
        except (asyncio.CancelledError, NameError):
            print("Tasks cancelled")
    
    finally:
        mqtt_manager.disconnect()
        wifi_manager.disconnect()
    
# Run with asyncio scheduling
asyncio.run(main())
