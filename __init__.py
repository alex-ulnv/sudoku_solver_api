import os

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

from .settings import DATABASE_FILE

app = Flask(__name__)

# TODO make this key exportable from the OS
app.config['SECRET_KEY'] = os.environ['API_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(DATABASE_FILE)

# Ensure deprecated functions are not used
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from .models import *
init_db()
from .routes import *

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)