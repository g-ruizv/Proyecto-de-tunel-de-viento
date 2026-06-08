from flask import request, Blueprint
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from . import app, db
from .models import Controller

controllerBP = Blueprint('controllers', __name__)

@controllerBP.route('/api/v1/fanWall/controllers/<id>', methods=['GET'])
@cross_origin()
def get_controller(id):
    # Intentar buscar tal cual llega
    controller = Controller.query.get(id)
    if controller:
        return {'id': controller.id, 'name': controller.name}

    # Probar la forma alternativa (':' <-> '-')
    alt = id.replace(':', '-') if ':' in id else id.replace('-', ':')
    controller = Controller.query.get(alt)
    if controller:
        return {'id': controller.id, 'name': controller.name}

    # No encontrado -> devolver JSON claro y 404 (evita AttributeError/500)
    return {'error': 'Controller not found'}, 404

@controllerBP.route('/api/v1/fanWall/controllers/<id>', methods=['POST'])
@cross_origin()
def add_controller(id):
    controller = Controller.query.get(id)
    if controller is None:
        controller = Controller(id=id)
        controller.name = request.json['name']
        db.session.add(controller)
        db.session.commit()
        return {'id': controller.id, 'name': controller.name}
    else:
        return {'error': 'Controller already exists'}

@controllerBP.route('/api/v1/fanWall/addMultipleControllers/', methods=['POST'])
@cross_origin()
def add_multiple_controllers():
    for controller in request.json['controllers']:
        controller_id = controller['id']
        controller_name = controller['name']
        controller = Controller.query.get(controller_id)
        if controller is None:
            controller = Controller(id=controller_id)
            controller.name = controller_name
            db.session.add(controller)
    db.session.commit()
    return {'success': 'Controllers added'}

@controllerBP.route('/api/v1/fanWall/controllers/<id>', methods=['DELETE'])
@cross_origin()
def delete_controller(id):
    controller = Controller.query.get(id)
    db.session.delete(controller)
    db.session.commit()
    return {'id': controller.id, 'name': controller.name, 'x_coordinate': controller.x_coordinate, 'y_coordinate': controller.y_coordinate}

@controllerBP.route('/api/v1/fanWall/controllers/<id>', methods=['PUT'])
@cross_origin()
def update_controller(id):
    controller = Controller.query.get(id)
    controller.name = request.json['name']
    db.session.commit()
    return {'id': controller.id, 'name': controller.name}
