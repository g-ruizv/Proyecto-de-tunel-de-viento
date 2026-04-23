import threading
from flask_socketio import emit
from . import mqtt_client, app, socketio
import time
last_speeds = {}
def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with result code {reason_code}")
    client.subscribe('fanWall/wall/control')
    client.subscribe('fanWall/wall/status')
    client.subscribe('fanWall/wall/id')

def on_message(client, userdata, msg):
    if msg.topic == 'fanWall/wall/id' and msg.payload.decode('utf-8') != 'get':
        print(f"Received message from {msg.topic}: {msg.payload}")
        with app.app_context():
            socketio.emit('fanId', {'id': msg.payload.decode('utf-8')})
    if msg.topic == 'fanWall/wall/status':
        print(f"Received message from {msg.topic}: {msg.payload}")
        msg.payload = msg.payload.decode('utf-8')
        message = msg.payload.split('/')
        if message[0] == 'Connected':
            with app.app_context():
                if message[1] not in last_speeds.keys():
                    last_speeds[message[1]] = 0
                send_mqtt_message('fanWall/wall/'+message[1], last_speeds[message[1]], mqtt_client)
                


def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")
    if rc != 0:
        print("Reconnecting")
        try_reconnect(client)

def try_reconnect(client):
    while True:
        try:
            client.reconnect()
            break
        except Exception as e:
            print(f"Reconnect failed: {e}")
            time.sleep(5)

def mqtt_thread():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect('broker.hivemq.com', 1883)
    print("Connected to MQTT broker")
    mqtt_client.loop_forever()

def start_mqtt():
    mqtt_thread_instance = threading.Thread(target=mqtt_thread)
    mqtt_thread_instance.daemon = True
    mqtt_thread_instance.start()

def mqtt_start():
    with app.app_context():
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect
        mqtt_client.connect('broker.hivemq.com', 1883)
        print("Connected to MQTT broker")
        mqtt_client.loop_start()

def send_mqtt_message(topic, message, client,setSpeed=False):
    with app.app_context():
        print(f"Sending message to {topic}: {message}")
        client.publish(topic, message)
        if setSpeed:
            last_speeds[topic.split('/')[-1]] = message
            print('last_speeds')
            print(last_speeds)
