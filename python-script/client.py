from mqtt_utils import Mqtt_Class
import json

if __name__ == '__main__':
    config_file = open('config.json')
    config = json.load(config_file)
    client1 = Mqtt_Class("client_1", config['ip'])
    client1.subscribe_topic("human_detected")
    client1.client.loop_forever()