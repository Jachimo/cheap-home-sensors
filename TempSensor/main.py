# TempSensor main.py

import machine
import config  # see config.py.sample
import network
import asyncio
import bme280_int
import collections
import ntptime

# Set up I2C for BME sensor (change pins and address as needed)
i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))
bme = bme280_int.BME280(i2c=i2c, address=0x76)

# Bring up WiFi interface in STA mode (client mode)
# Networks are specified in config.py
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


async def connect():
    print("Attempting new WiFi connection")
    targetssid = False
    targetauth = False
    scanout = wlan.scan()
    for ssid in [i[0].decode() for i in scanout]:
        if ssid in [i['SSID'] for i in config.WIFI_NETS]:
            targetssid = ssid
            targetauth = next(i['AUTH'] for i in config.WIFI_NETS if i['SSID'] is targetssid)
            print("Found network " + targetssid)
            break
        else:
            print("Found unknown network " + ssid)
            pass
    if targetssid:
        wlan.connect(targetssid, targetauth)
        await asyncio.sleep(5)  # allow time for DHCP setup
        print("Connect: ", wlan.ifconfig())


async def wifi_check_reconnect():
    while True:
        if not wlan.isconnected():
            await connect()
        await asyncio.sleep(30)


async def set_rtc_ntp():
    while True:
        ntptime.settime()  # default server is pool.ntp.org, set ntptime.host to change
        await asyncio.sleep(3600)  # update RTC hourly


async def read_temp():
    raw = bme.read_compensated_data()  # returns array for further processing
    tempc = raw[0] / 100  # temp in deg C
    tempf = (tempc * 1.8) + 32 
    return tempc, tempf


async def main():
    wifi_t = asyncio.create_task(wifi_check_reconnect())
    ntp_t = asyncio.create_task(set_rtc_ntp())
    
    while True:
        # finally read the damn temperature...
        temps = await read_temp()
        print(temps)  # DEBUG: Remove me later
        # TODO: Post to MQTT broker
        await asyncio.sleep(10)

# Run with asyncio scheduling
asyncio.run(main())
