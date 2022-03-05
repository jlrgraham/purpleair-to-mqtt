import requests
import paho.mqtt.client as mqtt
import certifi
import os
import random
import time
import json


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        publish_purpleair_config()
        publish_ha_discovery()
    else:
        print(f"Failed to connect, rc: {rc}")


def on_message(client, userdata, msg):
    pass



PURPLEAIR_HOSTNAME = os.getenv("PURPLEAIR_HOSTNAME", default="purpleair")
PURPLEAIR_FETCH_INTERVAL = os.getenv("PURPLEAIR_FETCH_INTERVAL", 60)
PURPLEAIR_MQTT_PREFIX = os.getenv("PURPLEAIR_MQTT_PREFIX", "purpleair")

MQTT_BROKER = os.getenv("MQTT_BROKER", default="mqtt")
MQTT_PORT = os.getenv("MQTT_PORT", default=8883)
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", default=f"purpleair_to_mqtt-{random.randint(0, 1000)}")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", default=None)
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", default=None)

HA_DISCOVERY_PREFIX = os.getenv("HA_DISCOVERY_PREFIX", "ha-discovery")

CONFIG_DATA_KEYS = [
    "Geo", "hardwarediscovered", "hardwareversion", "Id", "lat", "lon", "SensorId", "ssid", "version",
]
ENABLED_HA_DISCOVERY_KEYS = {
  "current_dewpoint_f": {
      "ha_domain": "sensor",
      "ha_device_class": "temperature",
      "ha_name": "Dewpoint",
      "ha_unit_of_meas": "°F",
  },
  "current_humidity": {
      "ha_domain": "sensor",
      "ha_device_class": "humidity",
      "ha_name": "Humidity",
      "ha_unit_of_meas": "%",
  },
  "current_temp_f": {
      "ha_domain": "sensor",
      "ha_device_class": "temperature",
      "ha_name": "Temperature",
      "ha_unit_of_meas": "°F",
  },
  "p25aqic": {},
  "p25aqic_b": {},
  "p_0_3_um": {
      "ha_domain": "sensor",
      "ha_name": ".3um Partical Count A",
      "ha_unit_of_meas": "um/dl",
  },
  "p_0_3_um_b": {
      "ha_domain": "sensor",
      "ha_name": ".3um Partical Count B",
      "ha_unit_of_meas": "um/dl",
  },
  "p_0_5_um": {
      "ha_domain": "sensor",
      "ha_name": ".5um Partical Count A",
      "ha_unit_of_meas": "um/dl",
  },
  "p_0_5_um_b": {
      "ha_domain": "sensor",
      "ha_name": ".5um Partical Count B",
      "ha_unit_of_meas": "um/dl",
  },
  "p_1_0_um": {
      "ha_domain": "sensor",
      "ha_name": "1um Partical Count A",
      "ha_unit_of_meas": "um/dl",
  },
  "p_1_0_um_b": {
      "ha_domain": "sensor",
      "ha_name": "1um Partical Count B",
      "ha_unit_of_meas": "um/dl",
  },
  "p_2_5_um": {
      "ha_domain": "sensor",
      "ha_name": "2.5um Partical Count A",
      "ha_unit_of_meas": "um/dl",
  },
  "p_2_5_um_b": {
      "ha_domain": "sensor",
      "ha_name": "2.5um Partical Count B",
      "ha_unit_of_meas": "um/dl",
  },
  "p_5_0_um": {
      "ha_domain": "sensor",
      "ha_name": "5um Partical Count A",
      "ha_unit_of_meas": "um/dl",
  },
  "p_5_0_um_b": {
      "ha_domain": "sensor",
      "ha_name": "5um Partical Count B",
      "ha_unit_of_meas": "um/dl",
  },
  "p_10_0_um": {
      "ha_domain": "sensor",
      "ha_name": "10um Partical Count A",
      "ha_unit_of_meas": "um/dl",
  },
  "p_10_0_um_b": {
      "ha_domain": "sensor",
      "ha_name": "10um Partical Count B",
      "ha_unit_of_meas": "um/dl",
  },
  "pm1_0_atm": {
      "ha_domain": "sensor",
      "ha_name": "1.0um Mass A",
      "ha_unit_of_meas": "ug/m3",
  },
  "pm1_0_atm_b": {
      "ha_domain": "sensor",
      "ha_name": "1.0um Mass B",
      "ha_unit_of_meas": "ug/m3",
  },
  "pm1_0_cf_1": {},
  "pm1_0_cf_1_b": {},
  "pm2.5_aqi": {
      "ha_domain": "sensor",
      "ha_device_class": "aqi",
      "ha_name": "AirQuality A",
      "ha_unit_of_meas": "AQI",
  },
  "pm2.5_aqi_b": {
      "ha_domain": "sensor",
      "ha_device_class": "aqi",
      "ha_name": "AirQuality B",
      "ha_unit_of_meas": "AQI",
  },
  "pm2_5_atm": {
      "ha_domain": "sensor",
      "ha_name": "2.5um Mass A",
      "ha_unit_of_meas": "ug/m3",
  },
  "pm2_5_atm_b": {
      "ha_domain": "sensor",
      "ha_name": "2.5um Mass B",
      "ha_unit_of_meas": "ug/m3",
  },
  "pm2_5_cf_1": {},
  "pm2_5_cf_1_b": {},
  "pm10_0_atm": {
      "ha_domain": "sensor",
      "ha_name": "10.0um Mass A",
      "ha_unit_of_meas": "ug/m3",
  },
  "pm10_0_atm_b": {
      "ha_domain": "sensor",
      "ha_name": "10.0um Mass B",
      "ha_unit_of_meas": "ug/m3",
  },
  "pm10_0_cf_1": {},
  "pm10_0_cf_1_b": {},
  "pressure": {
      "ha_domain": "sensor",
      "ha_device_class": "pressure",
      "ha_name": "Pressure",
      "ha_unit_of_meas": "mbar",
  },
}


class PurpleAirSensor(object):
    def __init__(self, hostname):
        self.__hostname__ = hostname
        self.__url__ = f"http://{PURPLEAIR_HOSTNAME}/json?live=true"
        self.__config__ = None
        self.__data__ = {}
        self.__data_timestamp__ = 0

        try:
            self.fetch_purpleair_data()
        except Exception:
            pass


    def fetch_purpleair_data(self):
        r = requests.get(self.__url__)

        if r.ok:
            self.__data__ = r.json()
            self.__config__ = {k: v for k, v in self.__data__.items() if k in CONFIG_DATA_KEYS}
            self.__data_timestamp__ = time.time()
        else:
            self.__data__ = {}
            self.__data_timestamp__ = 0


    def config(self):
        if self.__config__ is None:
            self.fetch_purpleair_data()
        return self.__config__


    def data(self):
        if self.__data__ is None or (time.time() > self.__data_timestamp__ + 60):
            self.fetch_purpleair_data()
        return self.__data__

    
    def sensor_topic_name(self):
        simple_sensor_id = self.__data__["SensorId"].replace(":", "")
        return f"purpleair-{simple_sensor_id}"



def publish_ha_discovery():
    sensor_topic_name = purpleair_sensor.sensor_topic_name()
    sensor_id = purpleair_sensor.__data__["SensorId"]

    for key, config in ENABLED_HA_DISCOVERY_KEYS.items():
        if "ha_domain" not in config:
            continue

        topic_base = f"{PURPLEAIR_MQTT_PREFIX}/{sensor_topic_name}"
        discovery_topic = f"{HA_DISCOVERY_PREFIX}/{config['ha_domain']}/{sensor_topic_name}-{key}/config"

        discovery_data = {
            "~": topic_base,
            "name": f"PurpleAir {sensor_id} {config['ha_name']}",
            "uniq_id": f"{sensor_topic_name}-{key}",
            "unit_of_meas": config["ha_unit_of_meas"],
            "stat_t": f"{topic_base}/data/{key}",
            "stat_cla": "measurement",
            "avty_t": f"{topic_base}/online",
            "pl_avail": "true",
            "pl_not_avail": "false",
            "dev": {
                "mf": "Purple Air, Inc.",
                "mdl": "PurpleAir PA-II-SD",
                "sw": purpleair_sensor.__data__["version"],
                "name": f"PurpleAir {sensor_id}",
                "ids": [sensor_id],
                "cns": [
                    ["mac", sensor_id]
                ],
                "cu": f"http://{PURPLEAIR_HOSTNAME}/",
            },
        }

        if "ha_device_class" in config.keys():
            discovery_data["dev_cla"] = config["ha_device_class"]

        client.publish(discovery_topic, json.dumps(discovery_data))


def publish_purpleair_config():
    config_topic = f"{PURPLEAIR_MQTT_PREFIX}/{purpleair_sensor.sensor_topic_name()}/config"
    result = client.publish(config_topic, str(purpleair_sensor.config()))


def publish_purpleair_data():
    mqtt_prefix = f"{PURPLEAIR_MQTT_PREFIX}/{purpleair_sensor.sensor_topic_name()}/data"

    for key, value in purpleair_sensor.data().items():
        topic = f"{mqtt_prefix}/{key}"
        result = client.publish(topic, value)
        if result != 0:
            pass # Handle error


def run():
    if MQTT_USERNAME is not None and MQTT_PASSWORD is not None:
        print(f"Connect as: {MQTT_USERNAME}")
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    will_topic = f"{PURPLEAIR_MQTT_PREFIX}/{purpleair_sensor.sensor_topic_name()}/online"

    client.on_connect = on_connect
    client.on_message = on_message

    if MQTT_PORT == 8883:
        client.tls_set(certifi.where())

    client.will_set(will_topic, payload="false", retain=True)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.loop_start()

    client.publish(will_topic, "true", retain=True)

    while True:
        print("publish_purpleair_data()")
        publish_purpleair_data()
        time.sleep(PURPLEAIR_FETCH_INTERVAL)


if __name__ == "__main__":
    if PURPLEAIR_HOSTNAME is None:
        raise Exception("PURPLEAIR_HOSTNAME must be defined.")
    if MQTT_BROKER is None:
        raise Exception("MQTT_BROKER must be defined.")

    purpleair_sensor = PurpleAirSensor(PURPLEAIR_HOSTNAME)
    client = mqtt.Client(MQTT_CLIENT_ID)

    run()