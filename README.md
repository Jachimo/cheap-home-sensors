Cheap Home Sensors
==================

> Inexpensive, networked, indoor sensors for home automation and monitoring.


## TempSensor (ESP8266 + BME280)

A wireless indoor air sensor, written using MicroPython for the ESP8266 and the
Bosch BME280 I2C temp/humid sensor.


### Links / Resources

* [Evernote Notes Page][EN] - Login required, not public
* [How to Install MicroPython][inst] - Good "getting started" tutorial
* [Thonny IDE][thonny] - Python/MicroPython IDE; easier than setting up VSCode
  with MicroPython support
* [Getting Started with MQTT on ESP32/ESP8266][rnt] - Uses the uPyCraft IDE and
  the `umqttsimple` library.  I can verify that this code does work, but it has
  inlined WiFi credentials and is probably best used as a starting point.
* [ESP8266 with BME280 using Arduino IDE][rnt2] - Uses Arduino instead of
  MicroPython but uses the modern BME280 sensor.
* [MicroPython: MQTT – Publish BME280 Sensor Readings][rnt3] - Very close to
  my goal of a very inexpensive temperature sensor with the 8266!
* [MicroPython Asynchronous MQTT][mqttas] - Modern library for reliable MQTT
  client operation; avoids some failure modes of the official uP library.

[EN]: https://share.evernote.com/note/1eaa817e-7288-409e-be1a-0f192c8e4d94
[inst]: https://www.kevsrobots.com/blog/how-to-install-micropython.html
[thonny]: https://thonny.org/
[rnt]: https://randomnerdtutorials.com/micropython-mqtt-esp32-esp8266/
[rnt2]: https://randomnerdtutorials.com/esp8266-bme280-arduino-ide/
[rnt3]: https://randomnerdtutorials.com/micropython-mqtt-publish-bme280-esp32-esp8266/
[mqttas]: https://github.com/peterhinch/micropython-mqtt/tree/master


### Environment Setup

1. Install Thonny: `pip3 install thonny` *should* work, or alternately they have
   a one-line installer for most Linux platforms:  
   `bash <(wget -O - https://thonny.org/installer-for-linux)`  
   On MacOS, the .pkg installer seems to be more reliable, and brings its own
   Python 3.10 instance with it.
2. If needed, install the appropriate USB/Serial adapter chip drivers.


### Hardware Setup

* The code assumes that the BME sensor is connected via I2C to pins 4 and 5.
  Specifically: `sda=machine.Pin(4), scl=machine.Pin(5)`
