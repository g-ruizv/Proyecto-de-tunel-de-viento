import threading
import time
from flask_socketio import emit
from . import mqtt_client, app, socketio

last_speeds = {}

# El mismo broker que tiene la placa ESP32 por defecto
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected to MQTT broker with result code {reason_code}")
    # Suscribirse a los tópicos del túnel de viento
    client.subscribe('fanWall/wall/control')
    client.subscribe('fanWall/wall/status')
    client.subscribe('fanWall/wall/id')

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    
    # 1. Recepción de ID
    if topic == 'fanWall/wall/id' and payload != 'get':
        print(f"Received ID from {topic}: {payload}")
        with app.app_context():
            socketio.emit('fanId', {'id': payload})
            
    # 2. Recepción de Estado (Status)
    elif topic == 'fanWall/wall/status':
        print(f"Received status from {topic}: {payload}")
        message = payload.split('/')
        
        # Si la placa avisa que se acaba de conectar
        if len(message) > 1 and message[0] == 'Connected':
            mac_address = message[1]  # usamos el formato tal cual llegó
            with app.app_context():
                # Inicializar velocidad si no existe
                if mac_address not in last_speeds:
                    last_speeds[mac_address] = 0
                
                # Re-enviar la última velocidad guardada a la placa recién conectada
                send_mqtt_message(f'fanWall/wall/{mac_address}', last_speeds[mac_address], client)

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")
    if rc != 0:
        print("Unexpected disconnection. Reconnecting...")
        try_reconnect(client)

def try_reconnect(client):
    while True:
        try:
            client.reconnect()
            break
        except Exception as e:
            print(f"Reconnect failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# Función única y limpia para iniciar MQTT
def mqtt_start():
    with app.app_context():
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect
        
        # Conectar al MISMO broker que la placa
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        print(f"Connecting to MQTT broker: {MQTT_BROKER}")
        mqtt_client.loop_start()

def send_mqtt_message(topic, message, client, setSpeed=False):
    with app.app_context():
        print(f"Sending message to {topic}: {message}")
        client.publish(topic, str(message))
        
        if setSpeed:
            mac_address = topic.split('/')[-1]
            last_speeds[mac_address] = message
            print(f'last_speeds updated: {last_speeds}')