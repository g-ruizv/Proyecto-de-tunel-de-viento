import threading
from time import sleep
from flask import request, Blueprint
from flask_cors import cross_origin
from . import db, mqtt_client
from .models import Preset
from .functions import generate_config_matrix, validate_json
from .mqtt import send_mqtt_message
from .socket import send_fan_speed

presetsBP = Blueprint('presets', __name__)

preset_thread = None
stop_event = threading.Event()


# ------------------------------------------------------------
# Rutas de la API
# ------------------------------------------------------------

@presetsBP.route('/api/v1/fanWall/presets', methods=['GET'])
@cross_origin()
def get_presets():
    presets = Preset.query.all()
    return {'presets': [
        {'id': preset.id, 'name': preset.name, 'data': preset.data}
        for preset in presets
    ]}


@presetsBP.route('/api/v1/fanWall/presets/<id>', methods=['POST'])
@cross_origin()
def add_preset(id):
    preset = Preset.query.get(id)
    is_valid, error = validate_json(request.json['data'])
    if not is_valid:
        return {'error': error}
    if preset is None:
        preset = Preset(id=id)
        preset.name = request.json['name']
        preset.data = request.json['data']
        db.session.add(preset)
        db.session.commit()
        return {'id': preset.id, 'name': preset.name, 'data': preset.data}
    else:
        return {'error': 'Preset already exists'}


@presetsBP.route('/api/v1/fanWall/presets', methods=['POST'])
@cross_origin()
def add_new_preset():
    is_valid, error = validate_json(request.json['data'])
    if not is_valid:
        print(error)
        return {'error': error}
    preset = Preset()
    preset.name = request.json['name']
    preset.data = request.json['data']
    db.session.add(preset)
    db.session.commit()
    return {'id': preset.id, 'name': preset.name, 'data': preset.data}


@presetsBP.route('/api/v1/fanWall/presets/<id>', methods=['DELETE'])
@cross_origin()
def delete_preset(id):
    preset = Preset.query.get(id)
    if preset:
        db.session.delete(preset)
        db.session.commit()
        return {'id': preset.id, 'name': preset.name, 'data': preset.data}
    return {'error': 'Preset not found'}, 404


@presetsBP.route('/api/v1/fanWall/presets/<id>', methods=['GET'])
@cross_origin()
def get_preset(id):
    preset = Preset.query.get(id)
    if not preset:
        return {'error': 'Preset not found'}, 404
    return {'id': preset.id, 'name': preset.name, 'data': preset.data}


@presetsBP.route('/api/v1/fanWall/presets/same_size/<x>/<y>', methods=['GET'])
@cross_origin()
def get_presets_of_size(x, y):
    presets = Preset.query.all()
    result = []
    for preset in presets:
        # Verificar que el preset tenga la estructura esperada
        if preset.data and 'frames' in preset.data and len(preset.data['frames']) > 0:
            matrix = preset.data['frames'][0].get('matrix')
            if matrix and len(matrix) > 0 and len(matrix[0]) > 0:
                if len(matrix) == int(y) and len(matrix[0]) == int(x):
                    result.append({'id': preset.id, 'name': preset.name, 'data': preset.data})
    return {'presets': result}


# ------------------------------------------------------------
# Ejecución y parada de presets
# ------------------------------------------------------------

def _run_preset_worker(preset, matrix, stop_event):
    """
    Worker que ejecuta la línea de tiempo del preset.
    preset.data debe tener la clave 'timeline' (lista de pasos).
    Cada paso debe tener 'time' (milisegundos) y velocidades por ID de controlador (ej. '1': 50).
    matrix es la disposición (lista de listas con IDs de controladores, 0 para vacío).
    """
    timeline = preset.data.get('timeline', [])
    if not timeline:
        print("El preset no tiene 'timeline'")
        return

    while not stop_event.is_set():
        for step in timeline:
            if stop_event.is_set():
                break

            # Recorrer cada celda de la matriz de disposición
            for i in range(len(matrix)):
                for j in range(len(matrix[i])):
                    controller_id = matrix[i][j]
                    if controller_id == 0:
                        continue
                    # Obtener velocidad del step usando el ID como string
                    speed = step.get(str(controller_id), 0)
                    # Enviar comando MQTT
                    controller_name = f'modulo-{controller_id}'
                    send_mqtt_message(f'fanWall/wall/{controller_name}', speed, mqtt_client)
                    # Emitir por SocketIO (si se usa)
                    send_fan_speed(controller_id, speed)

            # Esperar el tiempo indicado (milisegundos -> segundos)
            sleep(step.get('time', 0)) # segundos


@presetsBP.route('/api/v1/fanWall/presets/<presetId>/configuration/<configId>', methods=['GET'])
@cross_origin()
def run_preset(presetId, configId):
    global preset_thread, stop_event

    # Obtener el preset
    preset = Preset.query.get(presetId)
    if not preset:
        return {'error': 'Preset not found'}, 404

    # Validar que el preset tenga timeline
    if not preset.data or 'timeline' not in preset.data:
        return {'error': 'Preset missing "timeline" key'}, 400

    # Obtener la matriz de disposición desde la configuración
    matrix = generate_config_matrix(configId)
    if matrix is None:
        return {'error': 'Configuration matrix not found or invalid'}, 400

    # Si ya hay un hilo corriendo, detenerlo antes de iniciar otro
    if preset_thread and preset_thread.is_alive():
        stop_event.set()
        preset_thread.join(timeout=1.0)

    stop_event.clear()
    preset_thread = threading.Thread(target=_run_preset_worker, args=(preset, matrix, stop_event))
    preset_thread.daemon = True
    preset_thread.start()

    return {'status': 'Preset running'}


@presetsBP.route('/api/v1/fanWall/presets/<presetId>/configuration/<configId>/stop', methods=['GET'])
@cross_origin()
def stop_preset(presetId, configId):
    global stop_event
    stop_event.set()
    # Opcional: esperar a que el hilo termine realmente
    # if preset_thread and preset_thread.is_alive():
    #     preset_thread.join(timeout=1.0)
    return {'status': 'Preset stopped'}