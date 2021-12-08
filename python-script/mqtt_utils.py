import paho.mqtt.client as mqtt
import time
import json

class Mqtt_Class:
    def __init__(self, client_id, ip):
        print("initializing class")
        self.broker_address=ip
        self.client_id = client_id
        self.client = mqtt.Client(self.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_address, port=1883)

    def on_message(self, client, userdata, message):
        print("message received " ,str(message.payload.decode("utf-8")))
        print("message topic=",message.topic)
        print("message qos=",message.qos)
        print("message retain flag=",message.retain)
        if message.topic == "human_detected":
            tracked_info = str(message.payload.decode("utf-8"))
            print(tracked_info)

    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("connected to mqtt broker Returned code=",rc)
        else:
            print("Bad connection Returned code=",rc)

    def subscribe_topic(self, topic):
        print("Subscribing to topic ",topic)
        self.client.subscribe(topic)

    def publish_topic(self, topic, payload):
        print("Publishing message to topic ",topic)
        self.client.publish(topic,payload)