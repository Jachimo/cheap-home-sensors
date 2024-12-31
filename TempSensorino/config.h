// config.h

#ifndef CONFIG_H
#define CONFIG_H

#include <arduino_secrets.h>

// WiFi credentials
const char* ssid = SECRET_WIFI_SSID;
const char* password = SECRET_WIFI_KEY;

// MQTT broker configuration
const char* mqtt_server = SECRET_MQTT_BROKER_ADDR;
const int mqtt_port = 1883;  // Default MQTT port
const char* mqtt_user = "";  // Optional: set to "" if no username
const char* mqtt_password = "";  // Optional: set to "" if no password
const char* topic_bme280_c = "sensor/bme280/temperature_c";  // TODO: fix these to use hardware ID...
const char* topic_bme280_f = "sensor/bme280/temperature_f";
const char* topic_ds18b20_c = "sensor/ds18b20/temperature_c";
const char* topic_ds18b20_f = "sensor/ds18b20/temperature_f";

#endif // CONFIG_H
