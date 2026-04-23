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

def preset_frame_element_count(matrix):
    count = 0
    for row in matrix:
        count += len(row)
    return count


def is_preset_frame_rectangle(matrix):
    xSize, ySize = get_dimensions_from_preset(matrix)
    return preset_frame_element_count(matrix) == xSize * ySize

def validate_json(json):
    print('xdd')
    if 'frames' not in json or not isinstance(json['frames'], list):
        return False, 'frames must be a list'
    
    if len(json['frames']) == 0:
        return False, 'frames must have at least one element'
    
    cols, rows = get_dimensions_from_preset(json['frames'][0]['matrix'])
    print(rows, cols)

    for frame in json['frames']:
        print(frame)
        if not is_preset_frame_rectangle(frame['matrix']):
            return False, 'all frames must be rectangles'

        if 'matrix' not in frame:
            return False, 'matrix must be a key in each frame'
        
        if not isinstance(frame['matrix'], list):
            return False, 'matrix must be a list'
        
        if len(frame['matrix']) != rows:
            return False, 'all matrices must have the same number of rows'
        
        if len(frame['matrix'][0]) != cols:
            return False, 'all matrices must have the same number of columns'
        
        for row in frame['matrix']:
            if not all(isinstance(x, int) for x in row):
                return False, 'all elements in the matrix must be integers'
        
    
    return True, None
