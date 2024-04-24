from flask import Flask
from flask import render_template, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

controllers_configurations  = db.Table('controllers_configurations',
    db.Column('controller_id', db.String(80), db.ForeignKey('controller.id'), primary_key=True),
    db.Column('configuration_id', db.Integer, db.ForeignKey('configuration.id'), primary_key=True),
    db.Column('x_coordinate', db.Integer, nullable=False),
    db.Column('y_coordinate', db.Integer, nullable=False)
)

class Controller(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<Controller %r>' % self.name
    
class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    controllers = db.relationship('Controller', lazy='subquery', secondary=controllers_configurations, backref=db.backref('configurations', lazy=True))

def check_database():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if 'controller' in tables:
        return True
    else:
        return False

#controller1 = Controller(id='24:6F:28:A2:EE:68', name='Controller 1')

# Create a new Configuration
#config1 = Configuration(name='Configuration 1')
#config2 = Configuration(name='Configuration 2')

# Add controllers to configurations with coordinates
with app.app_context():
    if not check_database():
        db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/fanWall/controllers', methods=['GET'])
@cross_origin()
def get_controllers():
    controllers = Controller.query.all()
    return {'controllers': [controller.id for controller in controllers]}

@app.route('/api/v1/fanWall/controllers/<id>', methods=['POST'])
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
    


@app.route('/api/v1/fanWall/controllers/<id>', methods=['DELETE'])
@cross_origin()
def delete_controller(id):
    controller = Controller.query.get(id)
    db.session.delete(controller)
    db.session.commit()
    return {'id': controller.id, 'name': controller.name, 'x_coordinate': controller.x_coordinate, 'y_coordinate': controller.y_coordinate}

@app.route('/api/v1/fanWall/configurations', methods=['GET'])
@cross_origin()
def get_configurations():
    configurations = Configuration.query.all()
    return {'configurations': [configuration.name for configuration in configurations]}

@app.route('/api/v1/fanWall/configurations/<id>', methods=['POST'])
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

@app.route('/api/v1/fanWall/configurations/<id>', methods=['DELETE'])
@cross_origin()
def delete_configuration(id):
    configuration = Configuration.query.get(id)
    db.session.delete(configuration)
    db.session.commit()
    return {'id': configuration.id, 'name': configuration.name}

@app.route('/api/v1/fanWall/configurations/<id>', methods=['GET'])
@cross_origin()
def get_configuration(id):
    configuration = Configuration.query.get(id)
    return {'id': configuration.id, 'name': configuration.name, 'controllers': [controller.name for controller in configuration.controllers]}

@app.route('/api/v1/fanWall/configurations/<config_id>/add_controller/<controller_id>', methods=['POST'])
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

@app.route('/api/v1/fanWall/configurations/<config_id>/remove_controller/<controller_id>', methods=['DELETE'])
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

@app.route('/api/v1/fanWall/configurations/<config_id>/controllers', methods=['GET'])
@cross_origin()
def get_controllers_from_configuration(config_id):
    configuration = Configuration.query.get(config_id)
    
    if configuration is None:
        return {'error': 'Configuration not found'}
    
    controllers = configuration.controllers
    return {
        'configuration_id': config_id,
        'controllers': [controller.id for controller in controllers]
    }

@app.route('/api/v1/fanWall/configurations/<config_id>/controllers/<controller_id>', methods=['GET'])
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


if __name__ == '__main__':
    app.run(debug=True)
