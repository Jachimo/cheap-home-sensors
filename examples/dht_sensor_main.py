# MQTT temperature monitor and transmitter
# https://RandomNerdTutorials.com/micropython-mqtt-publish-dht11-dht22-esp32-esp8266/

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
from machine import Pin
import dht
esp.osdebug(None)
import gc

gc.collect()

ssid = 'MyWiFiSSID'
password = 'MyP@SSW0rd'
mqtt_server = '192.168.1.150'

client_id = ubinascii.hexlify(machine.unique_id())

topic_pub_temp = b'sensor/' + client_id + '/temperature'
topic_pub_hum = b'sensor/' + client_id + '/humidity'

last_message = 0
message_interval = 60

# First, disable the built-in AP
ap = network.WLAN(network.AP_IF)
ap.active(False)

# Then connect as a station to an existing network
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  # what to do if not connected...
  pass

print('Connection successful')

# GPIO 13 (Pin 13) is D7 on the Wemos D1
# See https://randomnerdtutorials.com/esp8266-pinout-reference-gpios/
sensor = dht.DHT22(Pin(13))

def connect_mqtt():
  global client_id, mqtt_server
  client = MQTTClient(client_id, mqtt_server)
  #client = MQTTClient(client_id, mqtt_server, user=your_username, password=your_password)
  client.connect()
  print('Connected to %s MQTT broker' % (mqtt_server))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

def read_sensor():
  try:
    sensor.measure()
    temp = sensor.temperature()  # reads in Celsius by default
    # uncomment for Fahrenheit
    temp = temp * (9/5) + 32.0
    hum = sensor.humidity()
    if (isinstance(temp, float) and isinstance(hum, float)) or (isinstance(temp, int) and isinstance(hum, int)):
      temp = (b'{0:3.1f}'.format(temp))
      hum =  (b'{0:3.1f}'.format(hum))
      return temp, hum
    else:
      return('Invalid sensor readings.')
  except OSError as e:
    return('Failed to read sensor.')

try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    if (time.time() - last_message) > message_interval:
      temp, hum = read_sensor()
      print(f'Publishing {temp} to {topic_pub_temp}')
      client.publish(topic_pub_temp, temp)
      print(f'Publishing {hum} to {topic_pub_hum}')
      client.publish(topic_pub_hum, hum)
      last_message = time.time()
  except OSError as e:
    restart_and_reconnect()
