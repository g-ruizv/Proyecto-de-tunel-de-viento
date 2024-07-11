from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import joinedload
from flask_socketio import SocketIO
from flask_cors import CORS
import paho.mqtt.client as mqttPaho
import threading
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)
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
    app.register_blueprint(user_blueprint)
    app.register_blueprint(main_blueprint)

    mqtt.mqtt_start()
    return app
