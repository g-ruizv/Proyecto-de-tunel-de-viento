from . import app, db
from .models import Configuration, Controller, controllers_configurations
from .queries import *




def generate_config_matrix(config_id):
    controllers = get_matrix_from_config(config_id)
    corners = get_config_corners(config_id)
    print('corners')
    print(corners)
    if is_config_rectangle(config_id):
        xSize, ySize = get_size_of_config(config_id)
        matrix = [[None for _ in range(xSize)] for _ in range(ySize)]
        for controller_coord in controllers:
            matrix[int((controller_coord.y_coordinate-corners[1])/2)][int((controller_coord.x_coordinate-corners[0])/2)] = controller_coord[0].id
        return matrix
    else:
        return None
    
def get_dimensions_from_preset(matrix):
    xSize = len(matrix[0])
    ySize = len(matrix)
    return (xSize, ySize)
