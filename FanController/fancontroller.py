# fancontroller.py
# Implements a Fan class for controlling multi-speed fan motors via GPIO relays

import machine
import asyncio

import config


class Fan:
    def __init__(self, RELAYS=config.RELAYS) -> None:
        self.relays = {}
        for k, v in RELAYS.items():
            self.relays[k] = machine.Pin(v, machine.Pin.OUT)
        self.state = "UNKNOWN"
        self.speed = None

    async def fan_stop(self) -> bool:
        for spd, pin in self.relays.items():
            pin.off()
        if self.speed:
            await asyncio.sleep(5)  # let fan spin down
        self.state = "STOPPED"
        self.speed = 0
        return True

    async def fan_speed(self, speed=None) -> int:
        if speed == None:
            return self.speed  # if no arguments, return current speed
        if speed != None and speed not in range(0,5):
            raise ValueError("Speed value out of range (0-4)")
        if self.speed == 0:  # if fan is currently stopped
            self.speed = 1   # prevent infinite recursion
            self.fan_start(1)  # 1 sec at max torque
        if speed == 1:
            self.relays["med"].off()
            self.relays["high"].off()
            self.relays["turbo"].off()
            await asyncio.sleep(0.1)
            self.relays["low"].on()
        elif speed == 2:
            self.relays["low"].off()
            self.relays["high"].off()
            self.relays["turbo"].off()
            await asyncio.sleep(0.1)
            self.relays["med"].on()
        elif speed == 3:
            self.relays["low"].off()
            self.relays["med"].off()
            self.relays["turbo"].off()
            await asyncio.sleep(0.1)
            self.relays["high"].on()
        elif speed == 4:
            self.relays["low"].off()
            self.relays["med"].off()
            self.relays["high"].off()
            await asyncio.sleep(0.1)
            self.relays["turbo"].on()
        else:
            self.fan_stop()  # for speed=0
            return 0
        self.state = "RUNNING"
        self.speed = speed
        return self.speed

    async def fan_start(self, t):
        """To get fan moving, use max speed/torque for t seconds"""
        self.fan_speed(4)
        self.state = "STARTING"
        await asyncio.sleep(t)  # variable fan-startup delay
