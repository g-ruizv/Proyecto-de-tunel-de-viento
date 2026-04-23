from flask import request, Blueprint
from flask_cors import cross_origin
from . import app, db
from .models import Configuration, Controller, controllers_configurations

controllers_configurationsBP = Blueprint('controllers_configurations', __name__)

@controllers_configurationsBP.route('/api/v1/fanWall/configurations/<config_id>/add_controller/<controller_id>', methods=['POST'])
@cross_origin()
def add_controller_to_configuration(config_id, controller_id):
    configuration = Configuration.query.get(config_id)
    controller = Controller.query.get(controller_id)
    
    if configuration is None:
        return {'error': 'Configuration not found'}
    elif controller is None:
        return {'error': 'Controller not found'}
    
    # Check if the controller is already associated with the configuration
    if db.session.query(controllers_configurations).filter_by(controller_id=controller_id, configuration_id=config_id).count() > 0:
        return {'error': 'Controller already added to the configuration'}
    
    # Assuming JSON data contains x_coordinate and y_coordinate
    x_coordinate = request.json.get('x_coordinate')
    y_coordinate = request.json.get('y_coordinate')
    
    controller_coord = controllers_configurations.insert().values(controller_id=controller_id, configuration_id=config_id, x_coordinate=x_coordinate, y_coordinate=y_coordinate)
    db.session.execute(controller_coord)
    db.session.commit()
    
    return {
        'configuration_id': config_id,
        'controller_id': controller_id,
        'x_coordinate': x_coordinate,
        'y_coordinate': y_coordinate
    }

@controllers_configurationsBP.route('/api/v1/fanWall/configurations/create_with_controllers', methods=['POST'])
@cross_origin()
def create_configuration_with_controllers():
    configuration = Configuration()
    configuration.name = request.json['name']
    db.session.add(configuration)
    
    for controller_id in request.json['controllers']:
        controller = Controller.query.get(controller_id)
        if controller is None:
            return {'error': 'Controller not found'}
        
        x_coordinate = request.json['controllers'][controller_id].get('x')
        y_coordinate = request.json['controllers'][controller_id].get('y')
        
        controller_coord = controllers_configurations.insert().values(controller_id=controller_id, configuration_id=configuration.id, x_coordinate=x_coordinate, y_coordinate=y_coordinate)
        db.session.execute(controller_coord)
    
    db.session.commit()
    
    return {
        'configuration_id': configuration.id,
        'name': configuration.name,
        'controllers': request.json['controllers']
    }

@controllers_configurationsBP.route('/api/v1/fanWall/configurations/<config_id>/controllers', methods=['PATCH'])
@cross_origin()
def update_configuration(config_id):
    configuration = Configuration.query.get(config_id)
    if not configuration:
        return {'error': 'Configuration not found'}, 404
    
    print(request.json)
    
    updated_controller_ids = set(request.json['controllers'].keys())
    
    # Update or add controller coordinates
    for controller_id in updated_controller_ids:
        controller = Controller.query.get(controller_id)
        if controller is None:
            return {'error': f'Controller {controller_id} not found'}, 404
        
        x_coordinate = request.json['controllers'][controller_id].get('x')
        y_coordinate = request.json['controllers'][controller_id].get('y')
        
        controller_coord = db.session.query(controllers_configurations).filter_by(controller_id=controller_id, configuration_id=config_id).first()
        
        if controller_coord:
            db.session.query(controllers_configurations).filter_by(controller_id=controller_id, configuration_id=config_id).update({
                'x_coordinate': x_coordinate,
                'y_coordinate': y_coordinate
            })
        else:
            controller_coord = controllers_configurations.insert().values(
                controller_id=controller_id, 
                configuration_id=config_id, 
                x_coordinate=x_coordinate, 
                y_coordinate=y_coordinate
            )
            db.session.execute(controller_coord)
    
    # Delete controller coordinates that are not in the request
    all_coords = db.session.query(controllers_configurations).filter_by(configuration_id=config_id).all()
    for coord in all_coords:
        if coord.controller_id not in updated_controller_ids:
            db.session.query(controllers_configurations).filter_by(controller_id=coord.controller_id, configuration_id=config_id).delete()
    
    db.session.commit()
    
    return {
        'configuration_id': config_id,
        'controllers': request.json['controllers']
    }



@controllers_configurationsBP.route('/api/v1/fanWall/configurations/<config_id>/remove_controller/<controller_id>', methods=['DELETE'])
@cross_origin()
def remove_controller_from_configuration(config_id, controller_id):
    configuration = Configuration.query.get(config_id)
    controller = Controller.query.get(controller_id)
    
    if configuration is None:
        return {'error': 'Configuration not found'}
    elif controller is None:
        return {'error': 'Controller not found'}
    
    # Check if the controller is associated with the configuration
    controller_coord = db.session.query(controllers_configurations).filter_by(controller_id=controller_id, configuration_id=config_id).first()
    if controller_coord is None:
        return {'error': 'Controller not found in the configuration'}
    
    db.session.delete(controller_coord)
    db.session.commit()
    
    return {
        'configuration_id': config_id,
        'controller_id': controller_id
    }

@controllers_configurationsBP.route('/api/v1/fanWall/configurations/<config_id>/controllers', methods=['GET'])
@cross_origin()
def get_controllers_from_configuration(config_id):
    configuration = Configuration.query.get(config_id)
    
    if configuration is None:
        return {'error': 'Configuration not found'}
    
    controllers = configuration.controllers
    coordinateJson = {}
    for controller in controllers:
        controller_coord = db.session.query(controllers_configurations).filter_by(controller_id=controller.id, configuration_id=config_id).first()
        coordinateJson[controller.id] = {'x': controller_coord.x_coordinate, 'y': controller_coord.y_coordinate, 'name': controller.name}
    return {
        'name': configuration.name,
        'configuration_id': config_id,
        'controllers': coordinateJson
    }

@controllers_configurationsBP.route('/api/v1/fanWall/configurations/<config_id>/controllers/<controller_id>', methods=['GET'])
@cross_origin()
def get_controller_from_configuration(config_id, controller_id):
    configuration = Configuration.query.get(config_id)
    controller = Controller.query.get(controller_id)
    
    if configuration is None:
        return {'error': 'Configuration not found'}
    elif controller is None:
        return {'error': 'Controller not found'}
    
    controller_coord = db.session.query(controllers_configurations).filter_by(controller_id=controller_id, configuration_id=config_id).first()
    if controller_coord is None:
        return {'error': 'Controller not found in the configuration'}
    
    return {
        'configuration_id': config_id,
        'controller_id': controller_id,
        'x_coordinate': controller_coord.x_coordinate,
        'y_coordinate': controller_coord.y_coordinate
    }