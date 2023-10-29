import paho.mqtt.client as paho
from db_connector import DBConnector
# from utils import send_alert

db_con = DBConnector()

def on_message(self, userdata, msg):
        print(msg.topic + ": " + msg.payload.decode())
        payload_str = msg.payload.decode()
        data = payload_str.split("-")
        if msg.topic == 'RTS/verifiedMsg':
            db_con.insert_verification_details(data=data)
        elif msg.topic == 'RTS/recognizedMsg':
            db_con.insert_detection_details(data=data)

        # if msg.topic == 'RTS/SendAlert':
        #     # data should be ['Unauthorized', 'date-time-obj']
        #     send_alert(data)
    

class Subscriber:

    def __init__(self):
        self.client = paho.Client()
        self.host = "localhost"
        self.port = 1883
        self.keep_alive = 60
        self.client.on_message = on_message

        if self.client.connect(self.host, self.port, self.keep_alive) != 0:
            print("Error: Couldn't connect to MQTT Broker!")
            exit(-1)

    def get_client(self):
        return self.client
    
    def subscribe_to(self, topic):
        self.client.subscribe(topic=topic)
    
    def disconnect_client(self):
        self.client.disconnect()

if __name__ == '__main__':
    print("Initializing subscriber...")
    subscriber = Subscriber()
    
    print("Subscribering to topics.")
    subscriber.subscribe_to("RTS/verifiedMsg")
    # subscriber.subscribe_to("RTS/SendAlert")
    subscriber.subscribe_to("RTS/recognizedMsg")

    try:
        print("Press CTRL+ to exit...")
        subscriber.get_client().loop_forever()
        
    except Exception as e:
        print("Disconnecting from broker", e)

    finally:
        subscriber.disconnect_client()
        db_con.close_connection()