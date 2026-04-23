import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_cors import CORS
import paho.mqtt.client as mqttPaho
import threading
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(base_dir, 'static'),
    template_folder=os.path.join(base_dir, 'templates'),
    static_url_path='/static'
)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fanwall.db'
app.config['CORS_HEADERS'] = 'Content-Type'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'info'
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")
cors = CORS(app)
mqtt_client = mqttPaho.Client()

from app import models, users, controllers, configurations, mqtt, routes, socket, controllers_configurations, queries, presets, functions

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

def create_app():
    
    with app.app_context():
        models.db.create_all()

    from app.users import user as user_blueprint
    from app.routes import main as main_blueprint
    from app.controllers import controllerBP as controller_blueprint
    from app.controllers_configurations import controllers_configurationsBP as controllers_configurations_blueprint
    from app.configurations import configurationsBP as configurations_blueprint
    from app.presets import presetsBP as presets_blueprint
    app.register_blueprint(user_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(controller_blueprint)
    app.register_blueprint(controllers_configurations_blueprint)
    app.register_blueprint(configurations_blueprint)
    app.register_blueprint(presets_blueprint)


    mqtt.mqtt_start()
    print('MQTT Started')
    return app

