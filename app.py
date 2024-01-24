
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
app = Flask(__name__)

app.config['SECRET_KEY'] = 'c3b9f846dc80fec3c879218547d1c93843bf1140c5c99e8812550819509fa78fc41d93799fe12370'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)


