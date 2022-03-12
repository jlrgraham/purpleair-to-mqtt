import requests
import paho.mqtt.client as mqtt
import certifi
import os
import time
import json
import logging

from homeassistant.components.mqtt.abbreviations import ABBREVIATIONS as HA_MQTT_ABBREVIATIONS
from homeassistant.components.mqtt.abbreviations import DEVICE_ABBREVIATIONS as HA_MQTT_DEVICE_ABBREVIATIONS


logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter('%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)


HA_MQTT_TO_ABBREVIATIONS = {v: k for k, v in HA_MQTT_ABBREVIATIONS.items()}
HA_MQTT_TO_DEVICE_ABBREVIATIONS = {v: k for k, v in HA_MQTT_DEVICE_ABBREVIATIONS.items()}

def abbreviate_ha_mqtt_keys(data):
    def rendered_generator(data, parent_key=None):
        # Quick wrapper to ensure we don't get back a data structure with a bunch
        # of nested generators, doesn't easily seralize.
        if isinstance(data, dict):
            return dict(generator(data, parent_key=parent_key))
        else:
            return data

    def generator(data, parent_key=None):
        # Adjust which table we lookup in based on the parent_key, this should be the
        # key matching the data block we receive.  HA stores the "device" abbreviations
        # in a separate varible.
        lookup_table = HA_MQTT_TO_ABBREVIATIONS
        if parent_key is not None and parent_key == "device":
            lookup_table = HA_MQTT_TO_DEVICE_ABBREVIATIONS

        for key, value in data.items():
            logger.debug(f"abbreviate_ha_mqtt_keys generator: {key} -> {lookup_table.get(key, key)}")
            yield lookup_table.get(key, key), rendered_generator(value, parent_key=key)

    return rendered_generator(data)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("MQTT: Connected to broker.")
        publish_purpleair_config()
        publish_ha_discovery()
    else:
        logger.error(f"MQTT: Failed to connect, rc: {rc}")


def on_message(client, userdata, msg):
    pass



PURPLEAIR_HOSTNAME = os.getenv("PURPLEAIR_HOSTNAME", default="purpleair")
PURPLEAIR_FETCH_INTERVAL = int(os.getenv("PURPLEAIR_FETCH_INTERVAL", 60))
PURPLEAIR_MQTT_PREFIX = os.getenv("PURPLEAIR_MQTT_PREFIX", "purpleair")

MQTT_BROKER = os.getenv("MQTT_BROKER", default="mqtt")
MQTT_PORT = os.getenv("MQTT_PORT", default=8883)
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", default=f"purpleair-to-mqtt")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", default=None)
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", default=None)

HA_DISCOVERY_PREFIX = os.getenv("HA_DISCOVERY_PREFIX", "homeassistant")

CONFIG_DATA_KEYS = [
    "Geo",
    "Id",
    "SensorId",
    "hardwarediscovered",
    "hardwareversion",
    "lat",
    "lon",
    "ssid",
    "version",
]

ENABLED_HA_DISCOVERY_KEYS = {
  "current_dewpoint_f": {
      "ha_domain": "sensor",
      "ha_name": "Dewpoint",
      "ha_discovery_config": {
          "device_class": "temperature",
          "unit_of_measurement": "°F",
      },
  },
  "current_humidity": {
      "ha_domain": "sensor",
      "ha_name": "Humidity",
      "ha_discovery_config": {
          "device_class": "humidity",
          "unit_of_measurement": "%",
      },
  },
  "current_temp_f": {
      "ha_domain": "sensor",
      "ha_name": "Temperature",
      "ha_discovery_config": {
          "device_class": "temperature",
          "unit_of_measurement": "°F",
      },
  },
  #"p25aqic": {},
  #"p25aqic_b": {},
  "p_0_3_um": {
      "ha_domain": "sensor",
      "ha_name": "0.3um Partical Count A",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_0_3_um_b": {
      "ha_domain": "sensor",
      "ha_name": "0.3um Partical Count B",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_0_5_um": {
      "ha_domain": "sensor",
      "ha_name": "0.5um Partical Count A",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_0_5_um_b": {
      "ha_domain": "sensor",
      "ha_name": "0.5um Partical Count B",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_1_0_um": {
      "ha_domain": "sensor",
      "ha_name": "1um Partical Count A",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_1_0_um_b": {
      "ha_domain": "sensor",
      "ha_name": "1um Partical Count B",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_2_5_um": {
      "ha_domain": "sensor",
      "ha_name": "2.5um Partical Count A",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_2_5_um_b": {
      "ha_domain": "sensor",
      "ha_name": "2.5um Partical Count B",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_5_0_um": {
      "ha_domain": "sensor",
      "ha_name": "5um Partical Count A",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_5_0_um_b": {
      "ha_domain": "sensor",
      "ha_name": "5um Partical Count B",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_10_0_um": {
      "ha_domain": "sensor",
      "ha_name": "10um Partical Count A",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "p_10_0_um_b": {
      "ha_domain": "sensor",
      "ha_name": "10um Partical Count B",
      "ha_discovery_config": {
          "unit_of_measurement": "um/dl",
          "enabled_by_default": "false",
      },
  },
  "pm1_0_atm": {
      "ha_domain": "sensor",
      "ha_name": "1.0um Mass A",
      "ha_discovery_config": {
          "unit_of_measurement": "ug/m3",
          "enabled_by_default": "false",
      },
  },
  "pm1_0_atm_b": {
      "ha_domain": "sensor",
      "ha_name": "1.0um Mass B",
      "ha_discovery_config": {
          "unit_of_measurement": "ug/m3",
          "enabled_by_default": "false",
      },
  },
  #"pm1_0_cf_1": {},
  #"pm1_0_cf_1_b": {},
  "pm25_aqi": {
      "ha_domain": "sensor",
      "ha_name": "AirQuality A",
      "ha_discovery_config": {
          "device_class": "aqi",
          "unit_of_measurement": "AQI",
      },
  },
  "pm25_aqi_b": {
      "ha_domain": "sensor",
      "ha_name": "AirQuality B",
      "ha_discovery_config": {
          "device_class": "aqi",
          "unit_of_measurement": "AQI",
      },
  },
  "pm2_5_atm": {
      "ha_domain": "sensor",
      "ha_name": "2.5um Mass A",
      "ha_discovery_config": {
          "unit_of_measurement": "ug/m3",
          "enabled_by_default": "false",
      },
  },
  "pm2_5_atm_b": {
      "ha_domain": "sensor",
      "ha_name": "2.5um Mass B",
      "ha_discovery_config": {
          "unit_of_measurement": "ug/m3",
          "enabled_by_default": "false",
      },
  },
  #"pm2_5_cf_1": {},
  #"pm2_5_cf_1_b": {},
  "pm10_0_atm": {
      "ha_domain": "sensor",
      "ha_name": "10.0um Mass A",
      "ha_discovery_config": {
          "unit_of_measurement": "ug/m3",
          "enabled_by_default": "false",
      },
  },
  "pm10_0_atm_b": {
      "ha_domain": "sensor",
      "ha_name": "10.0um Mass B",
      "ha_discovery_config": {
          "unit_of_measurement": "ug/m3",
          "enabled_by_default": "false",
      },
  },
  #"pm10_0_cf_1": {},
  #"pm10_0_cf_1_b": {},
  "pressure": {
      "ha_domain": "sensor",
      "ha_name": "Pressure",
      "ha_discovery_config": {
          "device_class": "pressure",
          "unit_of_measurement": "mbar",
      },
  },
}


class PurpleAirSensor(object):
    def __init__(self, hostname, cache_ttl=60):
        self.__hostname__ = hostname
        self.__url__ = f"http://{hostname}/json?live=true"
        self.__config__ = None
        self.__data__ = {}
        self.__data_timestamp__ = 0
        self.__data_cache_ttl__ = cache_ttl


    def fetch_purpleair_data(self):
        r = requests.get(self.__url__)

        if r.ok:
            jsondata = r.json()
            # Some keys contain characters that make them invalid for HA entity IDs
            # Filter them out
            key_fixes = []
            for key in jsondata.keys():
                if key.find('.') > -1:
                    new_key = key.replace('.', '')
                    key_fixes.append((key, new_key))

            for key, new_key in key_fixes:
                logger.info(f"PurpleAir JSON, patch key: {key} -> {new_key}")
                jsondata[new_key] = jsondata.pop(key)

            self.__data__ = jsondata
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
        if self.__data__ is None or (time.time() > self.__data_timestamp__ + self.__data_cache_ttl__):
            self.fetch_purpleair_data()
        return self.__data__

    
    def sensor_topic_name(self):
        simple_sensor_id = self.data()["SensorId"].replace(":", "")
        return f"purpleair-{simple_sensor_id}"



def publish_ha_discovery():
    sensor_topic_name = purpleair_sensor.sensor_topic_name()
    sensor_data = purpleair_sensor.data()
    sensor_id = sensor_data["SensorId"]

    for key, config in ENABLED_HA_DISCOVERY_KEYS.items():
        if "ha_domain" not in config:
            logger.warning(f"No 'ha_domain' setting found for {key}, skipping.")
            continue
        if "ha_name" not in config:
            logger.warning(f"No 'ha_name' setting found for {key}, skipping.")
            continue

        topic_base = f"{PURPLEAIR_MQTT_PREFIX}/{sensor_topic_name}"
        discovery_topic = f"{HA_DISCOVERY_PREFIX}/{config['ha_domain']}/{sensor_topic_name}-{key}/config"

        discovery_data = {
            "~": topic_base,
            "name": f"PurpleAir {sensor_id} {config['ha_name']}",
            "unique_id": f"{sensor_topic_name}-{key}",
            "state_topic": f"{topic_base}/data/{key}",
            "state_class": "measurement",
            "availability_topic": f"{topic_base}/online",
            "payload_available": "true",
            "payload_not_available": "false",
            "device": {
                "manufacturer": "Purple Air, Inc.",
                "model": sensor_data["hardwarediscovered"],
                "sw_version": sensor_data["version"],
                "name": f"PurpleAir {sensor_id}",
                "ids": [sensor_id],
                "connections": [
                    ["mac", sensor_id]
                ],
                "configuration_url": f"http://{PURPLEAIR_HOSTNAME}/",
            },
        }

        for discovery_key, value in config.get("ha_discovery_config", {}).items():
            discovery_data[discovery_key] = value

        abbreviated_discovery_data = abbreviate_ha_mqtt_keys(discovery_data)
        logger.debug(f"discovery_data: {json.dumps(discovery_data)}")
        logger.debug(f"abbreviated_discovery_data: {json.dumps(abbreviated_discovery_data)}")

        (result, mid) = client.publish(discovery_topic, json.dumps(discovery_data), retain=True)
        if result != 0:
            logger.error(f"MQTT: Error publishing discovery, result: {result}, topic: {discovery_topic}")
        else:
            logger.info(f"MQTT: Published discovery, topic: {discovery_topic}")


def publish_purpleair_config():
    config_topic = f"{PURPLEAIR_MQTT_PREFIX}/{purpleair_sensor.sensor_topic_name()}/config"
    result = client.publish(config_topic, str(purpleair_sensor.config()))


def publish_purpleair_data():
    mqtt_prefix = f"{PURPLEAIR_MQTT_PREFIX}/{purpleair_sensor.sensor_topic_name()}/data"

    for key, value in purpleair_sensor.data().items():
        topic = f"{mqtt_prefix}/{key}"
        (result, mid) = client.publish(topic, value)
        if result != 0:
            logger.error(f"MQTT: Error publishing data: {result}, topic: {topic}")


def run():
    if MQTT_USERNAME is not None and MQTT_PASSWORD is not None:
        logger.info(f"MQTT: Authentication enabled, connect as: {MQTT_USERNAME}")
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    will_topic = f"{PURPLEAIR_MQTT_PREFIX}/{purpleair_sensor.sensor_topic_name()}/online"

    client.on_connect = on_connect
    client.on_message = on_message

    if MQTT_PORT == 8883:
        logger.info("MQTT: Enable TLS.")
        client.tls_set(certifi.where())

    client.will_set(will_topic, payload="false", retain=True)

    logger.info(f"MQTT: Connect to {MQTT_BROKER}:{MQTT_PORT} ({MQTT_CLIENT_ID})")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.loop_start()

    (result, mid) = client.publish(will_topic, "true", retain=True)
    if result != 0:
        logger.error(f"MQTT: Error publishing to LWT, result: {result}, will_topic: {will_topic}")
    else:
        logger.info(f"MQTT: Publish online to LWT, will_topic: {will_topic}")

    last_publish = 0

    while True:
        if time.time() > last_publish + PURPLEAIR_FETCH_INTERVAL:
            logger.debug("publish_purpleair_data()")
            publish_purpleair_data()
            last_publish = time.time()
        time.sleep(1)


if __name__ == "__main__":
    if PURPLEAIR_HOSTNAME is None:
        raise Exception("PURPLEAIR_HOSTNAME must be defined.")
    if MQTT_BROKER is None:
        raise Exception("MQTT_BROKER must be defined.")

    purpleair_sensor = PurpleAirSensor(PURPLEAIR_HOSTNAME, cache_ttl=(PURPLEAIR_FETCH_INTERVAL - 1))
    client = mqtt.Client(MQTT_CLIENT_ID)

    run()
