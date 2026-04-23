from . import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql  import JSONB

controllers_configurations = db.Table(
    'controllers_configurations',
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

    def __repr__(self):
        return '<Configuration %r>' % self.name
    
class Preset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    data = db.Column(db.JSON, nullable=False)  # Using JSONB for JSON support in PostgreSQL

    def __repr__(self):
        return '<Preset %r>' % self.name
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
