from . import socketio, mqtt_client
from .mqtt import send_mqtt_message, last_speeds


@socketio.on('fanControl')
def handle_message(message):
    message_type = message.get('type')
    message_data = message.get('data')
    print('Received message:', message)

    if message_type == 'controller_information':
        print('Received controller information:', message_data)
        if message_data == 'get':
            send_mqtt_message('fanWall/wall/id', 'get', mqtt_client)

    elif message_type == 'command':
        print('Received command:', message_data)
        fanId = message_data.get('id')
        fanSpeed = message_data.get('speed')
        fanTopic = 'fanWall/wall/' + fanId
        send_mqtt_message(fanTopic, fanSpeed, mqtt_client,True)
        # Handle command
    elif message_type == 'config_update':
        print('Received config update:', message_data)
        # Handle configuration update
    elif message_type == 'activate':
        if message_data == 'start':
            send_mqtt_message('fanWall/wall/control', 'start', mqtt_client)
    elif message_type == 'controllerReset':
        if message_data == 'reset':
            send_mqtt_message('fanWall/wall/control', 'reset', mqtt_client)
            for fanId in last_speeds.keys():
                last_speeds[fanId] = 0
    else:
        print('Unknown message type')

def send_fan_speed(fanId, fanSpeed):
    socketio.emit('fanSpeed', {'id': fanId, 'speed': fanSpeed})


