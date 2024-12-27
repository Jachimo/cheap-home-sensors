# TempSensor

> A cheap room-temperature sensor using an ESP8266, a Bosch
> BME/BMP280, MQTT, and MicroPython.

Unlike similar $30 COTS sensors, these are cheap enough to have one
(or more) in every room of the house, allowing for fine-grained HVAC
control, presence detection, and other stuff.

![Sensor on Perfboard](https://github.com/Jachimo/cheap-home-sensors/blob/WIP/docs/images/proto_front.jpg)

The code is based on a number of examples and tutorials, including
Random Nerd Tutorials' [Getting Started with MQTT on
ESP32/ESP8266][rnt], [ESP8266 with BME280 using Arduino][rnt2], and
[MicroPython: MQTT Publish BME280 Sensor Readings][rnt3].

My code should be considered "developer use" on a good day; pull
requests for improvements and bugfixes are welcome.  It seems to work
well for me, but that's the extent of my testing.

## Parts & Supplies

* **ESP8266 Module** - I prefer the "D1 Mini" style boards for simple
sensors. 
    * If you are buying them in 2024, try to ensure you are getting
      the newer version with 4MB of flash, and not the older 1MB part;
      the 1MB versions require a special build of MicroPython in order
      to have `asyncio` support.  
    * See the `fw` directory in this repository if you need to use a
      1MB chip.

* **Temperature Sensor** - Several sensors are supported, although for
  general ambient-temperature sensing, I recommend the Bosch BME280.
  * **Bosch BME280** Sensor Module - The BME280 is a very small SMT part,
    but easily available as a prototyping module on a PCB.
    * Note that if you want relative humidity, the *BME* is the
      version with RH, not the BMP.
    * Currently they seem to be going for a [bit over
      $4/each][amztemp] on Amazon for a 3-pack if you are willing to
      take on some risk of counterfeits.  (At least returns are easy.)
    * [Adafruit][adatemp] and [Pimoroni][digitemp] both have very nice
      versions for a few dollars more. 
  * **DHT11 / DHT22** - These are older sensors and seem to be less
    accurate, although YMMV. 
  * **DS 1-Wire Sensors** - A bit slower, but these sensors tend to be
    physically smaller, so they're easier to use for remote
    monitoring, e.g. inside ductwork or even sealed into a probe for
    liquid temperature monitoring.

* You probably also want **some sort of substrate** to assemble
  everything on.  Use whatever you prefer.
    * I have found that sensors built on FR4-based perfboard with
      30AWG wire-wrap connections have stood up to significant
      vibration and general abuse, as long as the wires on the board
      are protected from snags. (Hot glue FTW.)

* Finally, **an enclosure** -- although I'm not one to judge, as I've
  had a bunch of these sensors hanging around in my house, dangling
  bare-assed from their MicroUSB connectors, for months at a time.
    * If you are buying an enclosure, note that the ESP module
      generates a fair bit of heat.  My scripts currently don't do any
      aggressive power-saving (device sleep, etc.) so the module gets
      noticeably warm.


[afh]: https://www.adafruit.com/product/2471
[amz]: https://www.amazon.com/ACEIRMC-ESP8266-Internet-Development-Compatible/dp/B09H6K2JQY
[amztemp]: https://www.amazon.com/Podazz-Temperature-Humidity-High-Precision-Atmospheric/dp/B0DCFXRZ1F
[adatemp]: https://www.adafruit.com/product/2652?gQT=2
[digitemp]: https://www.digikey.com/en/products/detail/pimoroni-ltd/PIM411/9808364
[amzperf]: https://www.amazon.com/Prototyping-Circuit-Breadboards-Envistia-Mall/dp/B07RC68D5C
[wikiwire]: https://en.wikipedia.org/wiki/Wire_wrap
[thingencl]: https://www.thingiverse.com/thing:3947394


## Hardware Setup

* The sensor needs two I2C bus lines (clock and data), power, and
  ground.
* The code assumes that the BME sensor is connected via I2C to pins 4
  and 5.  (As `sda=machine.Pin(4), scl=machine.Pin(5)`)
  * If you want to use different pins, just change them in `main.py`.


## Networking Setup

Open the `config.py.example` file, save it as `config.py`, and modify
as appropriate with your WiFi network(s), MQTT server (aka broker),
and other values as desired.

## Deploying

[Copy all `.py` files to an ESP8266][rshell] flashed with MicroPython
and trigger a reset.  The script prints basic status to the REPL
output, typically visible on the USB UART.

[rshell]: https://github.com/dhylands/rshell

## Background Reading and Notes

* **Project-Specific** 
  * [Evernote Notes Page][EN] - Login required, not public
* **MicroPython**
  * [How to Install MicroPython][inst] - Good "getting started" tutorial
  * [Thonny IDE][thonny] - Python/MicroPython IDE; easier than setting up VSCode
    with MicroPython support
  * [MicroPython: MQTT – Publish BME280 Sensor Readings][rnt3] - Very close to
    my goal of a very inexpensive temperature sensor with the 8266!
  * [MicroPython Asynchronous MQTT][mqttas] - Modern library for reliable MQTT
    client operation; avoids some failure modes of the official uP
    library.
* **Python** (Generally)
  * [An In-Depth Guide to `asyncio` and `await` in Python][await] - Good general
    reference on the Python/uP asyncio library.
* **ESP8266 Embedded System**
  * [Getting Started with MQTT on ESP32/ESP8266][rnt] - Uses the uPyCraft IDE and
    the `umqttsimple` library.  I can verify that this code does work, but it has
    inlined WiFi credentials and is probably best used as a starting point.
  * [ESP8266 with BME280 using Arduino IDE][rnt2] - Uses Arduino instead of
    MicroPython but uses the modern BME280 sensor.
* **Other Hardware**
  * [Bosch BME280 Datasheet][bosch] - Official documentation on the
    BME280 sensor and its outputs.

[EN]: https://share.evernote.com/note/1eaa817e-7288-409e-be1a-0f192c8e4d94
[inst]: https://www.kevsrobots.com/blog/how-to-install-micropython.html
[thonny]: https://thonny.org/
[await]: https://medium.com/@danielwume/an-in-depth-guide-to-asyncio-and-await-in-python-059c3ecc9d96
[rnt]: https://randomnerdtutorials.com/micropython-mqtt-esp32-esp8266/
[rnt2]: https://randomnerdtutorials.com/esp8266-bme280-arduino-ide/
[rnt3]: https://randomnerdtutorials.com/micropython-mqtt-publish-bme280-esp32-esp8266/
[mqttas]: https://github.com/peterhinch/micropython-mqtt/tree/master
[bosch]: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
