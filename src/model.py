from src import db

class User(db.Model):
    __tablename__ = "Users"

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class Project(db.Model):
    __tablename__ = 'Projects'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean(), default=False)
    actions = db.relationship('Action', backref='Users')

class Action(db.Model):
    __tablename__= 'Actions'

    id = db.Column(db.Integer(), primary_key=True)
    project_id = db.Column(db.Integer(), db.ForeignKey('Projects.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(100), nullable=False)