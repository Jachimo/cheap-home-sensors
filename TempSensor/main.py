# TempSensor main.py - https://github.com/Jachimo/cheap-home-sensors
#  Note: asyncio support is required!
#
# Development version 20250630

from typing import Union

import machine
import network
import asyncio
import collections
import ntptime
import time
import gc

from wifimanager import WiFiManager
from mqttmanager import MQTTManager

from tempsensors import BMESensor
from tempsensors import DHT11Sensor
from tempsensors import DHT22Sensor
from tempsensors import DS18Sensor

import config  # see config.py.sample


async def set_rtc_ntp(wifi_manager: WiFiManager) -> None:
    """ Synchronize device clock via NTP at specified intervals. """
    ntptime.host = "pool.ntp.org"
    while True:
        gc.collect()
        if wifi_manager.is_connected:
            ntptime.settime()
            print(f"RTC successfully set via NTP from {ntptime.host}")
            await asyncio.sleep(3600)  # update RTC hourly
        else:
            print(f"RTC clock set failed (tried {ntptime.host}")
            await asyncio.sleep(60)    # if network is down, check again in a minute


async def acquire_transmit(wifi_manager: WiFiManager, 
                           sensor: Union[BMESensor, DHT11Sensor, DHT22Sensor, DS18Sensor],  # TODO: any subclass of TempSensor
                           mqtt_manager: MQTTManager, 
                           topic_base: str = "sensor", 
                           addl_values: Union[dict, bool] = False) -> None:
    """ Acquire data from sensors and transmit to the MQTT broker via WiFi. """
    while True:
        gc.collect()

        if not wifi_manager.is_connected:
            await asyncio.sleep(30)  # Wait for WiFi retry
            await wifi_manager.scan_and_connect()
            continue

        if not mqtt_manager.is_connected:
            await asyncio.sleep(30)  # wait for MQTT retry
            await mqtt_manager.connect()
            continue 
        
        try:
            svalues = await sensor.read()
        except Exception as e:
            print("Exception while reading sensor")
            print(e)
            await asyncio.sleep(15)  # delay before sensor reset and retry
            try:
                sensor.reset()
                continue
            except Exception as e:
                print(f"Exception while attempting to reset {sensor.sensor_type}")
                print(e)
                raise
        
        if addl_values:
            for k in addl_values:
                svalues[k] = addl_values[k]
        
        if 'id' in svalues:
            # If the sensor has its own ID, use it (trimmed to last 8 chars)
            pub_id = svalues['id'][-8:]
        else:
            # But if not, publish directly under the tx unit ID
            pub_id = config.SENSOR_ID
        
        for key, value in svalues.items():
            mqtt_manager.publish(f"{topic_base}/{pub_id}/{key}", str(value))
            print(f"{topic_base}/{pub_id}/{key} =", str(value))
        
        await asyncio.sleep(30)  # Sensor reading interval


async def main():
    """ Main entrypoint """
    print(f"Sender {config.SENSOR_ID} starting up...")
    wifi_manager = WiFiManager(config.WIFI_NETS)
    mqtt_manager = MQTTManager(config.MQTT_ADDR)

    addl_values = {}
    addl_values['location'] = config.LOCATION
    if config.DEBUG:
        addl_values['free_memory'] = gc.mem_free()
        # TODO: Also add unit's IP address if DEBUG is enabled

    if not await wifi_manager.scan_and_connect():
        print("No known networks in range, will continue to retry")

    tasks = []
    try:
        wifi_t = asyncio.create_task(wifi_manager.monitor_connection())
        ntp_t = asyncio.create_task(set_rtc_ntp(wifi_manager))
    
        # TODO: There is almost certainly a more elegant way to do this,
        #  involving matching the config dicts in the config file to the available
        #  tempsensor subclasses... but: 
        if "BME" in config.SENSORS.keys():
            sensor_bme = BMESensor(config.SENSORS['BME']['scl_pin'], 
                                config.SENSORS['BME']['sda_pin'], 
                                config.SENSORS['BME']['i2c_address'])
            bme_t = asyncio.create_task(acquire_transmit(wifi_manager, sensor_bme, mqtt_manager))
            tasks.append(bme_t)
        if "DHT11" in config.SENSORS.keys():
            sensor_dht11 = DHT11Sensor(config.SENSORS['DHT11']['sensor_pin'])
            dht11_t = asyncio.create_task(acquire_transmit(wifi_manager, sensor_dht11, mqtt_manager))
            tasks.append(dht11_t)
        if "DHT22" in config.SENSORS.keys():
            sensor_dht22 = DHT22Sensor(config.SENSORS['DHT22']['sensor_pin'])
            dht22_t = asyncio.create_task(acquire_transmit(wifi_manager, sensor_dht22, mqtt_manager))
            tasks.append(dht22_t)
        if "DS18" in config.SENSORS.keys():
            sensor_ds18  = DS18Sensor(config.SENSORS['DS18']['sensor_pin']) 
            ds_t  = asyncio.create_task(acquire_transmit(wifi_manager, sensor_ds18, mqtt_manager))
            tasks.append(ds_t)
                
        await asyncio.gather(tasks, return_exceptions = False)

    except (Exception, KeyboardInterrupt) as e:
        print("STOP: Terminating and resetting")
        print(e)
        try:
            for t in tasks:
                t.cancel()
        except (asyncio.CancelledError, NameError):
            print("Tasks cancelled")
    
    finally:
        mqtt_manager.disconnect()
        wifi_manager.disconnect()
        
        print("System resetting!")
        machine.reset()
    
# Run with asyncio scheduling
asyncio.run(main())
