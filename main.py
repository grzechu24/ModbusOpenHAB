#!/usr/bin/python3

import time
import signal
import sys
import logging
from pathlib import Path
import paho.mqtt.client as mqtt
import minimalmodbus
from device import ThesslaDevice, ModbusDevice

thessla = ThesslaDevice("Rekuperator")
solar = ModbusDevice("Falownik")

# Logging
Path("/var/log/modbus-mqtt").mkdir(exist_ok=True)
logging.basicConfig(filename=f"/var/log/modbus-mqtt/modbus-mqtt-openhab.log",
                    filemode='a',
                    format='# %(asctime)s : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    # encoding='utf-8',
                    level=logging.DEBUG)


def signal_handler(signum, frame):
    if client is not None:
        client.loop_stop()
        client.disconnect()
        logging.info("Closing MQTT client")
    logging.info("Bye..!")
    sys.exit(0)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(mqtt_client, userdata, flags, rc):
    logging.info("MQTT: Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    subscribe_topic = f"{thessla.getMqttTopic()}-S/+"
    mqtt_client.subscribe(subscribe_topic)
    logging.info(f"Subscribing topic: {subscribe_topic}")


def on_message(mqtt_client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server"""
    lista_topic = str(msg.topic).split('/')
    lista_topic.append(str(msg.payload, "utf-8"))
    # print(F"MQTT received: {lista_topic[0]}/{lista_topic[1]}/{lista_topic[2]}")
    # Rekuperator
    if "REKU" in lista_topic[0]:
        thessla.receive(lista_topic[1], lista_topic[2])
    # Falownik
    elif "FV" in lista_topic[0]:
        solar.receive(lista_topic[1], lista_topic[2])


def sendValues(dict_val_send: dict, publish_prefix: str):
    """Sends given topics and values in dictionary via MQTT"""
    # if dict is not empty
    if dict_val_send is not False:
        for (pub_topic, pub_value) in dict_val_send.items():
            full_topic = publish_prefix + "-P/" + pub_topic
            # publish message
            if pub_value is not None:
                client.publish(full_topic, pub_value)


# Signals declarations
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Connect to MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.10", 1883, 60)
client.loop_start()     # starting non-blocking new thread

# other variables
SLEEP_TIME_SEC = 1
send_all_counter = 0

while True:
    try:
        # ======= REKUPERATOR =========
        try:
            if thessla.isEnable():
                thessla.writeRegisters()
                sendValues(thessla.readRegisters(), thessla.getMqttTopic())
                # thessla.printDataTable()
                time.sleep(SLEEP_TIME_SEC)
        except minimalmodbus.NoResponseError:
            sendValues(thessla.setOffline(), thessla.getMqttTopic())

        # ========= FALOWNIK ==========
        try:
            if solar.isEnable():
                sendValues(solar.readRegisters(), solar.getMqttTopic())
                # solar.printDataTable()
                time.sleep(SLEEP_TIME_SEC)
        except minimalmodbus.NoResponseError:
            sendValues(solar.setOffline(), solar.getMqttTopic())

        # Send all registers periodically
        send_all_counter += 1
        if send_all_counter >= 60:
            thessla.updateAllRegisters()
            solar.updateAllRegisters()
            send_all_counter = 0

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt!")
        signal_handler(None, None)
