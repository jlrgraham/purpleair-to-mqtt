FROM python:3-slim AS ha_wheel_builder

RUN apt-get update && apt-get install \
    -y --no-install-recommends \
    build-essential

RUN pip wheel homeassistant


FROM python:3-slim

RUN pip install requests paho-mqtt certifi

COPY --from=ha_wheel_builder /homeassistant-*.whl /
COPY --from=ha_wheel_builder /ciso8601-*.whl /
RUN pip install /homeassistant-*.whl /ciso8601-*.whl

COPY purpleair_to_mqtt.py /purpleair_to_mqtt.py

CMD ["/usr/local/bin/python", "/purpleair_to_mqtt.py"]
