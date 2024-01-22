from app import db
from datetime import datetime

Player = db.Table('Player', db.Column('id', db.Integer, primary_key=True),
                  db.Column("user", db.Integer, db.ForeignKey('user.id')),
                  db.Column("group", db.Integer, db.ForeignKey('group.id')))


class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    user = db.relationship('User', lazy='dynamic')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    password = db.Column(db.String)
    email = db.Column(db.String(120), unique=True)
    is_valid = db.Column(db.Boolean, default=False)
    rule = db.Column(db.Integer, db.ForeignKey('rule.id'), default=None)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)


class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    groups = db.relationship('Group', lazy='dynamic')


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    season = db.Column(db.Integer, db.ForeignKey('season.id'))

    players = db.relationship('User', secondary='Player', backref='group', lazy='dynamic')


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_accepted = db.Column(db.Boolean, default=False)
    result = db.Column(db.Boolean, default=None)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    first_player = db.Column(db.Integer, db.ForeignKey('Player.id', ))
    second_player = db.Column(db.Integer, db.ForeignKey('Player.id'))
