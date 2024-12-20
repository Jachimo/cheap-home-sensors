Cheap Home Sensors
==================

> Inexpensive, networked, indoor sensors for home automation and monitoring.


## TempSensor (ESP8266 + BME280)

A wireless indoor air sensor, written using MicroPython for the ESP8266 and the
Bosch BME280 I2C temp/humid sensor.


### Background Reading

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
  client operation; avoids some failure modes of the official uP
  library.
* [Bosch BME280 Datasheet][bosch] - Official documentation on the
  BME280 sensor and its outputs.

[EN]: https://share.evernote.com/note/1eaa817e-7288-409e-be1a-0f192c8e4d94
[inst]: https://www.kevsrobots.com/blog/how-to-install-micropython.html
[thonny]: https://thonny.org/
[rnt]: https://randomnerdtutorials.com/micropython-mqtt-esp32-esp8266/
[rnt2]: https://randomnerdtutorials.com/esp8266-bme280-arduino-ide/
[rnt3]: https://randomnerdtutorials.com/micropython-mqtt-publish-bme280-esp32-esp8266/
[mqttas]: https://github.com/peterhinch/micropython-mqtt/tree/master
[bosch]: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf

### Environment Setup

1. Install Thonny: `pip3 install thonny` *should* work, or alternately they have
   a one-line installer for most Linux platforms:  
   `bash <(wget -O - https://thonny.org/installer-for-linux)`  
   On MacOS, the .pkg installer seems to be more reliable, and brings its own
   Python 3.10 instance with it.
2. If needed, install the appropriate USB/Serial adapter chip drivers.


### Parts & Supplies

* **ESP8266 Module** - I prefer the "D1 Mini" style boards to the
  older 30-pin "NodeMCU" style ones for this type of application, as they are
  a bit smaller and tend to be less expensive.  If you're buying one
  in 2024, be sure it's a 4M flash version (unless you are sure you're
  comfortable with the older 2M version and you're getting them at a
  really great price).
    * The [Adafruit HUZZAH][afh] modules look particularly nice if you
      aren't pinching pennies, but they are about 5x the cost of the
      generic Chinese ones.
    * The generics are easily found [on Amazon][amz] (if that link is
      dead, just search for "ESP8266 D1") for under $3/each in
      quantities of 10, or slightly more if you prefer to only buy one
      or two.
    * Of course, AliExpress is your source for the cheapest examples,
      often under $2/each (as of late 2024) if you are willing to wait
      on shipping from China; US-warehouse stock seems to be about the
      same price as Amazon.  I have no recommended vendors; just
      search "ESP8266 D1" and pick one that doesn't seem *too* good to
      be true.
* **Bosch BME280 Sensor Module** - The BME280 is a very small SMT part, but
  easily available as a pre-soldered module with decoupling caps and a
  mounting hole or two.  Note that if you want relative humidity, be
  sure you're ordering the *BME* and not the *BMP* part, as the latter
  lacks it and just outputs zero for RH.  They work identically
  otherwise.
    * The Bosch sensor seems likely to be a target for counterfeiters,
      due to the number of essentially similar (but typically
      inferior) parts that exist that could be swapped in for the real
      thing, and its relatively high cost.  Proceed with caution.
    * Currently they seem to be going for a [bit over
      $4/each][amztemp] on Amazon for a 3-pack if you are willing to
      take on some risk of counterfeits.  (At least returns are easy.)
    * As usual, [Adafruit has a very high-quality module][adatemp]
      available at a somewhat premium price.
    * There's also a similarly-nice module from Pimoroni [available
      via Digikey][digitemp], which is particularly nice if you are already
      used to buying your parts there.
* You probably also want **some sort of substrate** to assemble everything
  on.  The world is your oyster here; use whatever you prefer.
    * A solderless breadboard will work fine for testing, but I prefer
      to assemble things on [cheap little perfboards][amzperf] with
      [wire-wrapped][wikiwire] connections.  
    * I have found that sensors built on FR4-based perfboard with
      30AWG wire-wrap connections have stood up to significant
      vibration and general abuse, as long as the wires on the board
      are protected from snags. (Hot glue FTW.)  Allegedly, wire-wrap
      construction was used on some ICBM components, so it can
      probably deal with being mounted on a fan, air filter, etc.
      (Although in fairness, the ICBM circuit only had to work *once*.)
* Finally, you probably want **an enclosure** -- although I'm not one
  to judge, as I've had a bunch of these sensors hanging around in my
  house, dangling bare-assed from their MicroUSB connectors, for
  months at a time.
    * If you are buying an enclosure, steer clear of anything that
      seals the temperature sensor in alongside the ESP module, since
      the latter generates a non-trivial amount of heat.
    * I've been experimenting with "stack effect" enclosures that have
      vents at the top and bottom, and with the sensor at the bottom
      and the ESP at the top.  In theory, the heat generated by the
      ESP should constantly pull in fresh air at the bottom, moving it
      across the sensor before it has a chance to get warm.
    * A 3-D printed enclosure with the sensor mounted on the outside,
      [like this one which uses the older DHT-11 sensor][thingencl],
      could be another option.


[afh]: https://www.adafruit.com/product/2471
[amz]: https://www.amazon.com/ACEIRMC-ESP8266-Internet-Development-Compatible/dp/B09H6K2JQY
[amztemp]: https://www.amazon.com/Podazz-Temperature-Humidity-High-Precision-Atmospheric/dp/B0DCFXRZ1F
[adatemp]: https://www.adafruit.com/product/2652?gQT=2
[digitemp]: https://www.digikey.com/en/products/detail/pimoroni-ltd/PIM411/9808364
[amzperf]: https://www.amazon.com/Prototyping-Circuit-Breadboards-Envistia-Mall/dp/B07RC68D5C
[wikiwire]: https://en.wikipedia.org/wiki/Wire_wrap
[thingencl]: https://www.thingiverse.com/thing:3947394


### Hardware Setup

* The code assumes that the BME sensor is connected via I2C to pins 4 and 5.
  Specifically: `sda=machine.Pin(4), scl=machine.Pin(5)`
