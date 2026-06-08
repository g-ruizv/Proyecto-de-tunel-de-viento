from . import app, db
from .models import Configuration, Controller, controllers_configurations
from .queries import *

def generate_config_matrix(config_id):
    relations = db.session.query(controllers_configurations).filter_by(configuration_id=config_id).all()
    if not relations:
        print(f"No relations for config {config_id}")
        return None

    # Obtener los nombres de las columnas del primer elemento
    first = relations[0]
    # Intentar detectar nombres de columnas
    if hasattr(first, 'x'):
        x_attr = 'x'
        y_attr = 'y'
    elif hasattr(first, 'x_coordinate'):
        x_attr = 'x_coordinate'
        y_attr = 'y_coordinate'
    elif hasattr(first, 'pos_x'):
        x_attr = 'pos_x'
        y_attr = 'pos_y'
    else:
        # Si no, asumimos que está en la posición 2 y 3 (pero es frágil)
        x_attr = None
        y_attr = None

    if x_attr is not None:
        max_x = max([getattr(r, x_attr) for r in relations])
        max_y = max([getattr(r, y_attr) for r in relations])
    else:
        # Fallback usando índices (suponiendo que la tabla tiene columnas: id, configuration_id, controller_id, x, y)
        max_x = max([r[3] for r in relations])
        max_y = max([r[4] for r in relations])

    matrix = [[0 for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    for rel in relations:
        if x_attr is not None:
            x = getattr(rel, x_attr)
            y = getattr(rel, y_attr)
        else:
            x = rel[3]
            y = rel[4]
        controller = db.session.get(Controller, rel.controller_id)
        if controller:
            try:
                cid = int(controller.name.split('-')[1])
            except:
                cid = controller.id
        else:
            cid = 0
        matrix[y][x] = cid

    print("Generated matrix:", matrix)
    return matrix
    
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
