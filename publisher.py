import paho.mqtt.client as paho

class Publisher:

    def __init__(self):
        self.client = paho.Client()
        self.host = "localhost"
        self.port = 1883
        self.keep_alive = 60

        if self.client.connect(self.host, self.port, self.keep_alive) != 0:
            print("Error: Couldn't connect to MQTT Broker!")
            exit(-1)
        else:
            print("Publisher connected to MQTT Broker!")

    def publish_msg(self, topic, message):
        qos = 0

        self.client.publish(topic,
                            message,
                            qos)
    
    def disconnect_client(self):
        self.client.disconnect()

# if __name__ == '__main__':
#     publisher = Publisher()
    
#     publisher.publish_msg(topic = "RTS/detection", message = "Hello there!")

#     publisher.disconnect_client()