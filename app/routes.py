from flask import Blueprint, render_template
from flask_login import login_required
from . import app, users

main = Blueprint('main', __name__)

@app.route('/')
@login_required
def index():
    return render_template('index.html')