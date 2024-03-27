from flask import Flask
from flask import render_template
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

controllers = db.Table('controllers',
    db.Column('controller_id', db.Integer, db.ForeignKey('controller.id'), primary_key=True),
    db.Column('configuration_id', db.Integer, db.ForeignKey('configuration.id'), primary_key=True)
)

class Controller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<Controller %r>' % self.name
    
class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    controllers = db.relationship('Controller', lazy='subquery', secondary=controllers, backref=db.backref('configurations', lazy=True))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/fanWall/controllers', methods=['GET'])
@cross_origin()
def get_controllers():
    controllers = Controller.query.all()
    return {'controllers': [controller.name for controller in controllers]}

@app.route('/api/v1/fanWall/controllers/<id>', methods=['POST'])
@cross_origin()
def add_controller(id):
    controller = Controller.query.get(id)
    if controller is None:
        controller = Controller(id=id)
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
    return {'id': controller.id, 'name': controller.name}

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


if __name__ == '__main__':
    app.run(debug=True)
