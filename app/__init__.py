from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from flask_socketio import SocketIO
from flask_cors import CORS
import paho.mqtt.client as mqttPaho
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)
socketio = SocketIO(app)
cors = CORS(app)
mqtt_client = mqttPaho.Client()

from app import models, controllers, configurations, mqtt, routes, socket, controllers_configurations, queries, presets, functions

def create_app():
    with app.app_context():
        models.db.create_all()

    mqtt.mqtt_start()
    return app
