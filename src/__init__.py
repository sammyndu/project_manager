from flask import Flask
from flask_sqlalchemy import SQLAlchemy, sqlalchemy

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile("config.py", silent=True)

db = SQLAlchemy(app)

from .user import Users
