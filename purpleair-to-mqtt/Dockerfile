FROM python:3-slim

RUN pip install requests paho-mqtt certifi

COPY purpleair_to_mqtt.py /purpleair_to_mqtt.py

CMD ["/usr/local/bin/python", "/purpleair_to_mqtt.py"]
