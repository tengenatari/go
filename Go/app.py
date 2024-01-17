from datetime import datetime
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
app = Flask(__name__)

app.config['SECRET_KEY'] = 'c3b9f846dc80fec3c879218547d1c93843bf1140c5c99e8812550819509fa78fc41d93799fe12370'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().create_from_db(User=User.query.filter(User.id == user_id).first())


def check_on_repeat(table, column, value, text):
    if table.query.filter(column == value).count() > 0:
        flash(text, category='error-msg')
        return True
    return False



Player = db.Table('Player', db.Column('ID', db.Integer, primary_key=True),
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

    first_player = db.Column(db.Integer, db.ForeignKey('player.id', ))
    second_player = db.Column(db.Integer, db.ForeignKey('player.id'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/groups')
def groups():
    return render_template('groups.html')


@app.route('/members')
@login_required
def members():
    return render_template("/members.html")


@app.route('/table.html')
def tables():
    return render_template("table.html")


@app.route('/authpage', methods=['GET', 'POST'])
def authorization():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(name=username).first()
        if check_password_hash(user.password, password):
            userlogin = UserLogin().create(user)
            login_user(user, userlogin)
            flash('Logged in successfully!', 'error-msg')
    return render_template('authpage.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        is_registered = True
        if len(request.form['username']) < 4:
            flash("Имя пользователя должно быть не менее 5 символов", category='error-msg')
            is_registered = False
        if len(request.form['password']) < 7:
            flash("Пароль должен быть не менее 8 символов", category='error-msg')
            is_registered = False
        if check_on_repeat(User, User.name, request.form['username'], 'Пользователь с таким именем уже зарегистрирован' ):
            is_registered = False
        if check_on_repeat(User, User.email, request.form['email'], 'Пользователь с такой почтой уже зарегистрирован'):
            is_registered = False
        if 'utmn.ru' not in request.form['email']:
            flash(message="Неверный формат почты, домен должен быть в формате utmn.ru", category='error-msg')
            is_registered = False
        if request.form['password'] != request.form['password-validation']:
            flash(message="Пароли не совпадают", category='error-msg')
            is_registered = False
        if is_registered:
            name = request.form['username']
            password = generate_password_hash(request.form['password'])
            email = request.form['email']

            user = User(name=name, password=password, email=email)

            db.session.add(user)
            db.session.commit()

    return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)
