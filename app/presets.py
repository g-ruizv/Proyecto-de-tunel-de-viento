import threading
from time import sleep
from flask import request
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from . import app, db, mqtt_client
from .models import Preset
from .functions import generate_config_matrix
from .mqtt import mqtt_client, send_mqtt_message

preset_thread = None
stop_event = threading.Event()


@app.route('/api/v1/fanWall/presets', methods=['GET'])
@cross_origin()
def get_presets():
    presets = Preset.query.all()
    return {'presets': [
        {'id':preset.id,'name':preset.name, 'data':preset.data} 
        for preset in presets
        ]}

@app.route('/api/v1/fanWall/presets/<id>', methods=['POST'])
@cross_origin()
def add_preset(id):
    preset = Preset.query.get(id)
    if preset is None:
        preset = Preset(id=id)
        preset.name = request.json['name']
        preset.data = request.json['data']
        db.session.add(preset)
        db.session.commit()
        return {'id': preset.id, 'name': preset.name, 'data': preset.data}
    else:
        return {'error': 'Preset already exists'}
    
@app.route('/api/v1/fanWall/presets/<id>', methods=['DELETE'])
@cross_origin()
def delete_preset(id):
    preset = Preset.query.get(id)
    db.session.delete(preset)
    db.session.commit()
    return {'id': preset.id, 'name': preset.name, 'data': preset.data}

@app.route('/api/v1/fanWall/presets/<id>', methods=['GET'])
@cross_origin()
def get_preset(id):
    preset = Preset.query.get(id)
    return {'id': preset.id, 'name': preset.name, 'data': preset.data}

@app.route('/api/v1/fanWall/presets/<presetId>/configuration/<configId>', methods=['GET'])
@cross_origin()
def run_preset(presetId, configId):
    global preset_thread, stop_event
    preset = Preset.query.get(presetId)
    matrix = generate_config_matrix(configId)

    stop_event.clear()

    preset_thread = threading.Thread(target=run_preset, args=(preset,matrix))
    preset_thread.start()
    return {'status': 'Preset running'}


@app.route('/api/v1/fanWall/presets/<presetId>/configuration/<configId>/stop', methods=['GET'])
@cross_origin()
def stop_preset(presetId, configId):
    global stop_event

    stop_event.set()

    return {'status': 'Preset stopped'}
    
    


def run_preset(preset,matrix):
    while not stop_event.is_set():
        for frame in preset.data['frames']:
            print(frame['matrix'])
            for i in range(len(frame['matrix'])):
                for j in range(len(frame['matrix'][i])):
                    print(i, j, frame['matrix'][i][j], matrix[i][j])
                    controllerId = matrix[i][j]
                    controllerSetSpeed = frame['matrix'][i][j]
                    send_mqtt_message('fanwall/wall/' + controllerId,controllerSetSpeed,mqtt_client)
            sleep(frame['time']/1000)   