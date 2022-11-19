# purpleair-to-mqtt

Bridge PurpleAir sensor data to [Home Assistant](https://www.home-assistant.io/) via [MQTT Discovery](https://www.home-assistant.io/docs/mqtt/discovery/).

## Usage

### Kubernetes StatefulSet

    ---
    apiVersion: apps/v1
    kind: StatefulSet
    metadata:
      name: purpleair-to-mqtt
    spec:
      selector:
        matchLabels:
          app: purpleair-to-mqtt
      replicas: 1
      template:
        metadata:
          labels:
            app: purpleair-to-mqtt
        spec:
          terminationGracePeriodSeconds: 0
          containers:
          - env:
            - name: PURPLEAIR_HOSTNAME
              value: 192.168.1.50
            - name: MQTT_CLIENT_ID
              value: purpleair-to-mqtt
            - name: MQTT_BROKER
              value: mqtt.broker.name.com
            - name: MQTT_USERNAME
              value: mqtt_user
            - name: MQTT_PASSWORD
              value: itsasecret
            - name: HA_DISCOVERY_PREFIX
              value: ha-discovery
            image: jlrgraham/purpleair-to-mqtt:latest
            imagePullPolicy: Always
            name: purpleair-to-mqtt
          restartPolicy: Always

## Settings

All settings are taken from environmental variables at runtime.

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `PURPLEAIR_HOSTNAME` | The hostname or IP address of the PurpleAir sensor. | `purpleair` |
| `PURPLEAIR_FETCH_INTERVAL` | The interval, in seconds, at which to fetch and publish data from the sensor. | 60 |
| `PURPLEAIR_MQTT_PREFIX` | The MQTT prefix under which to publish sensor data.  See MQTT Topics for more details. | `purpleair` |
| `MQTT_BROKER` | The hostname or IP of the MQTT broker. | `mqtt` |
| `MQTT_PORT` | The connection port on the MQTT broker.  If set to 8883 TLS is automatically used. | 8883 |
| `MQTT_CLIENT_ID` | The client name given to the MQTT broker.  See MQTT Connections for more details. | `purpleair-to-mqtt` |
| `MQTT_USERNAME` | The username for the MQTT broker. | `None` |
| `MQTT_PASSWORD` | The password for the MQTT broker. | `None` |
| `HA_DISCOVERY_ENABLED` | Enable publishing of HA discovery topics. | `True` |
| `HA_DISCOVERY_PREFIX` | The configured Home Assistant discovery prefix. | `homeassistant` |


### MQTT Connections

#### Authentication

Authentication will be attempted only if both `MQTT_USERNAME` and `MQTT_PASSWORD` are supplied.

#### Client ID

The MQTT client ID can be configured with the `MQTT_CLIENT_ID` variable.  This should generally be fixed for a given deployment.

#### TLS

If the MQTT broker port configuration is set to 8883 then the connector will automatically attempt to enable TLS for the connection to the broker.  The standard [Python certifi package](https://pypi.org/project/certifi/) will be used for CA roots, so public certs (ie: Let's Encrypt + others) should just work.

### MQTT Topics

There are two topic configuration controls: `PURPLEAIR_MQTT_PREFIX` and `HA_DISCOVERY_PREFIX`.

The `PURPLEAIR_MQTT_PREFIX` setting will control the top level prefix in MQTT used for PurpleAir data.  This is intended to be a namespace for PurpleAir sensors allowing for multiple to coexist and be discovered on a single broker.  Each sensor will have data published under `<PURPLEAIR_MQTT_PREFIX>/purpleair-<SENSOR_IDENTIFIER>` where `SENSOR_IDENTIFIER` is the hex only version of the sensor's MAC address.

Within the sensor's prefix in MQTT the following topics are published (example sensor with a MAC address of `00:1b:ad:c0:ff:ee`:

    purpleair/
        purpleair-001badc0ffee/
            config = JSON Object, select keys from sensor data
            data/
                p_0_3_um = 0.3um value A from the sensor
                p_0_3_um_b = 0.3um value B from the sensor
                ... = rest of the sensor values
            online = (true|false) the status of the sensor, registered with a LWT message on the broker

The `HA_DISCOVERY_PREFIX` setting should match [discovery prefix setting](https://www.home-assistant.io/docs/mqtt/discovery/#discovery_prefix) in Home Assistant.

## DockerHub Image

This script is available in a Docker image from: [https://hub.docker.com/repository/docker/jlrgraham/purpleair-to-mqtt/](https://hub.docker.com/repository/docker/jlrgraham/purpleair-to-mqtt/)
