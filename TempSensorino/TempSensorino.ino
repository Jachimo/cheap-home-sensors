// mqtt_temp_sender.ino
//  A quick-and-dirty sketch to read from one of several temperature sensors, and
//  post the result to an MQTT broker; for comparison to MicroPython versions
//
// See: https://github.com/Jachimo/cheap-home-sensors/

#include <Wire.h>            // I2C aka TwoWire library
#include <ESP8266WiFi.h>     // WiFi library for ESP8266
#include <PubSubClient.h>    // https://pubsubclient.knolleary.net/api

#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

#include <OneWire.h>
#include <DallasTemperature.h>

#include "config.h"  // Include the configuration file

// GPIO for the I2C bus (for BME280)
#define I2C_SDA 33
#define I2C_SCL 32

// GPIO for the OneWire sensor bus
#define ONE_WIRE_BUS 2

// Chip-specific hardware ID (used in MQTT topics)
String hardwareId = String(ESP.getChipId(), HEX);

// Create instances for WiFi and MQTT clients
WiFiClient    espClient;
PubSubClient  client(espClient);

// Create instances for BME280
TwoWire          I2CBUS = TwoWire(0);  // I2C Bus
Adafruit_BME280  bme;                  // BME280 sensor

// Create instances for DS18B20
OneWire            oneWire(ONE_WIRE_BUS);
DallasTemperature  ds18b20(&oneWire);

// Connect to WiFi
void setup_wifi() {
  delay(10);
  Serial.print("Connecting to ");
  Serial.print(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// Connect to MQTT broker
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    bool connected;

    // Connect with or without creds
    if (strlen(mqtt_user) > 0 && strlen(mqtt_password) > 0) {
      connected = client.connect("ESP8266Client", mqtt_user, mqtt_password);
    } else {
      connected = client.connect("ESP8266Client");
    }

    if (connected) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" will try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  Serial.setDebugOutput(true); // Enable debug output

  // Initialize I2C bus
  I2CBUS.begin(I2C_SDA, I2C_SCL, 100000);

  // Initialize WiFi
  setup_wifi();

  // Initialize MQTT
  client.setServer(mqtt_server, mqtt_port);

  // Initialize BME280 sensor
  bme.begin(0x76, &I2CBUS)
  Serial.println("BME280 sensor initialized successfully");

  // Initialize DS18B20 sensor
  ds18b20.begin();
  Serial.println("DS18B20 sensor initialized successfully");

  // Give time for the sensors to start up
  delay(1000);
}

void loop() {
  // Reconnect to MQTT if disconnected
  if (!client.connected()) {
    reconnect();
  }
  client.loop();  // Process queued MQTT messages

  // Read temperature from BME280 sensor
  float temperatureC_bme280 = bme.readTemperature();
  if (isnan(temperatureC_bme280)) {
    Serial.println("Failed to read temperature from BME280 sensor!");
  } else {
    float temperatureF_bme280 = temperatureC_bme280 * 1.8 + 32;

    // Publish BME280 temperature data
    char tempCStr_bme280[8];
    char tempFStr_bme280[8];
    dtostrf(temperatureC_bme280, 6, 2, tempCStr_bme280);
    dtostrf(temperatureF_bme280, 6, 2, tempFStr_bme280);

    if (!client.publish(topic_bme280_c, tempCStr_bme280)) {
      Serial.println("Failed to publish BME280 temperature_c data to MQTT");
    } else {
      Serial.print("BME280 Temperature (C) sent: ");
      Serial.println(tempCStr_bme280);
    }

    if (!client.publish(topic_bme280_f, tempFStr_bme280)) {
      Serial.println("Failed to publish BME280 temperature_f data to MQTT");
    } else {
      Serial.print("BME280 Temperature (F) sent: ");
      Serial.println(tempFStr_bme280);
    }
  }

  // Request temperature from DS18B20 sensor
  ds18b20.requestTemperatures();
  float temperatureC_ds18b20 = ds18b20.getTempCByIndex(0);
  if (temperatureC_ds18b20 == DEVICE_DISCONNECTED_C) {
    Serial.println("Failed to read temperature from DS18B20 sensor!");
  } else {
    float temperatureF_ds18b20 = temperatureC_ds18b20 * 1.8 + 32;

    // Publish DS18B20 temperature data
    char tempCStr_ds18b20[8];
    char tempFStr_ds18b20[8];
    dtostrf(temperatureC_ds18b20, 6, 2, tempCStr_ds18b20);
    dtostrf(temperatureF_ds18b20, 6, 2, tempFStr_ds18b20);

    if (!client.publish(topic_ds18b20_c, tempCStr_ds18b20)) {
      Serial.println("Failed to publish DS18B20 temperature_c data to MQTT");
    } else {
      Serial.print("DS18B20 Temperature (C) sent: ");
      Serial.println(tempCStr_ds18b20);
    }

    if (!client.publish(topic_ds18b20_f, tempFStr_ds18b20)) {
      Serial.println("Failed to publish DS18B20 temperature_f data to MQTT");
    } else {
      Serial.print("DS18B20 Temperature (F) sent: ");
      Serial.println(tempFStr_ds18b20);
    }
  }

  // Non-blocking delay
  static unsigned long lastMillis = 0;
  if (millis() - lastMillis > 30000) {
    lastMillis = millis();
  }
}
