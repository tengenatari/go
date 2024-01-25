from flask import Flask, render_template, request, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from checker import check_form
from main_request import *
from app import db, app, login_manager
from models import *


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().create(User.query.filter(User.id == user_id).first())


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/authpage')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html')


@app.route('/profile/games')
@login_required
def profile_games():
    return render_template('profile_games.html')


@app.route('/groups/<string:name_group>')
def groups(name_group):

    return render_template('groups.html', seasons = select_seasons())


@app.route('/games')
def view_games():
    return render_template('games.html')


@app.route('/about')
def games():
    return render_template('about.html')


@app.route('/members')
def members():
    return render_template("/members.html", members=select_users_data())


@app.route('/table.html')
def tables():
    return render_template("table.html")


@app.route('/authpage', methods=['GET', 'POST'])
def authorization():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(name=username).first()
        if user and check_password_hash(user.password, password):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect('/')
        else:
            flash('Неверное имя пользователя или пароль', 'error-msg')
    return render_template('authpage.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_2 = request.form['password-validation']

        if check_form(name, email, password, password_2):

            password = generate_password_hash(password)

            user = User(name=name, password=password, email=email)

            db.session.add(user)
            db.session.commit()

            flash('Вы успешно зарегистрированы! :)', category='success-msg')

            return redirect('/authpage')

    return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)