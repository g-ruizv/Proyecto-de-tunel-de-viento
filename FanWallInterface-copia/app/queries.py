from . import app, db
from sqlalchemy import func
from .models import Configuration, Controller, controllers_configurations

def get_matrix_from_config(config_id):
    with app.app_context():
        controller_configs = db.session.query(Controller, controllers_configurations).join(
            controllers_configurations,
            controllers_configurations.c.controller_id == Controller.id
        ).filter(
            controllers_configurations.c.configuration_id == config_id
        ).all()
        return controller_configs
    
def get_size_of_config(config_id):
    with app.app_context():
        result = db.session.query(
            func.max(controllers_configurations.c.x_coordinate) - func.min(controllers_configurations.c.x_coordinate),
            func.max(controllers_configurations.c.y_coordinate) - func.min(controllers_configurations.c.y_coordinate)
        ).filter(
            controllers_configurations.c.configuration_id == config_id
        ).one()

        print('resultSize')
        print(result)
        xSize = int(result[0]/2+1)
        ySize = int(result[1]/2+1)
        if xSize==0:
            xSize = 1
        if ySize==0:
            ySize = 1
        return xSize, ySize
    
def get_config_corners(config_id):
    with app.app_context():
        result = db.session.query(
            func.min(controllers_configurations.c.x_coordinate),
            func.min(controllers_configurations.c.y_coordinate),
            func.max(controllers_configurations.c.x_coordinate),
            func.max(controllers_configurations.c.y_coordinate)
        ).filter(
            controllers_configurations.c.configuration_id == config_id
        ).one()
        return result[0], result[1], result[2], result[3]
    
def get_controller_count(config_id):
    with app.app_context():
        result = db.session.query(
            func.count(controllers_configurations.c.controller_id)
        ).filter(
            controllers_configurations.c.configuration_id == config_id
        ).one()
        return result[0]
def is_config_square(config_id):
    xSize, ySize = get_size_of_config(config_id)
    controllerCount = get_controller_count(config_id)
    if controllerCount == 1:
        return True
    return xSize == ySize and controllerCount == xSize**2

def is_config_rectangle(config_id):
    xSize, ySize = get_size_of_config(config_id)
    print('xSize, ySize')
    print(xSize, ySize)
    controllerCount = get_controller_count(config_id)
    if controllerCount == 1:
        return True
    
    return controllerCount == xSize*ySize
