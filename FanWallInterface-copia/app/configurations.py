from flask import request, Blueprint
from flask_cors import cross_origin
from . import app, db
from .models import Configuration

configurationsBP = Blueprint('configurations', __name__)

@configurationsBP.route('/api/v1/fanWall/configurations', methods=['GET'])
@cross_origin()
def get_configurations():
    configurations = Configuration.query.all()
    return {'configurations': [
        {'id':configuration.id,'name':configuration.name} 
        for configuration in configurations
        ]}

@configurationsBP.route('/api/v1/fanWall/configurations/<id>', methods=['POST'])
@cross_origin()
def add_configuration(id):
    configuration = Configuration.query.get(id)
    if configuration is None:
        configuration = Configuration(id=id)
        configuration.name = request.json['name']
        db.session.add(configuration)
        db.session.commit()
        return {'id': configuration.id, 'name': configuration.name}
    else:
        return {'error': 'Configuration already exists'}

@configurationsBP.route('/api/v1/fanWall/configurations/<id>', methods=['DELETE'])
@cross_origin()
def delete_configuration(id):
    configuration = Configuration.query.get(id)
    db.session.delete(configuration)
    db.session.commit()
    return {'id': configuration.id, 'name': configuration.name}

@configurationsBP.route('/api/v1/fanWall/configurations/<id>', methods=['GET'])
@cross_origin()
def get_configuration(id):
    configuration = Configuration.query.get(id)
    return {'id': configuration.id, 'name': configuration.name, 'controllers': [controller.name for controller in configuration.controllers]}
