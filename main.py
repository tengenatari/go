from math import sqrt
from flask import Flask, render_template, request, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from checker import check_form
from main_request import *
from app import db, app, login_manager
from models import *
from typing import Callable
from functools import partial


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
    return render_template('profile.html', Database=Database)


@app.route('/profile/games')
@login_required
def profile_games():
    return render_template('game-req.html', Database=Database)


@app.route('/send-request', methods=['GET', 'POST'])
@login_required
def send_request():
    if request.method == 'POST':
        req = request.form
        user2 = req["user2"]
        if not(Database.create_game_request(current_user.get_user().id, user2)):
            flash(message='Вы находитесь в разных группах', category='msg-success')
    return redirect('/profile/games')


@app.route('/profile/join/group', methods=['GET', 'POST'])
@login_required
def send_request_join_group():
    if request.method == 'POST':
        if current_user.get_user().is_valid:
            flash("Вы успешно вступили в группу", category='msg-success')
        else:
            flash("Вы не можете вступить в группу, пока не подтвердите почту", category='error-msg')
    return redirect('/profile/games')


@app.route('/update-game/<string:query>', methods=['GET', 'POST'])
@login_required
def decline_game_request(query):
    if request.method == 'POST':
        req = request.form

        if query == "one":
            game_id = int(req["game_id"])
            if req["accept"] == "Принять":
                Database.update_obj(Game, Game.id, game_id, Game.is_accepted, True)
            elif req["accept"] == "Отклонить" or req["accept"] == "Отменить":
                Database.delete_obj(Game, Game.id, game_id)

            else:
                return redirect("404.html")
    return redirect('/profile/games')






@app.route('/groups/<int:group_id>')
def groups(group_id):
    matrix = Database.select_division_stat(group_id)
    count = int(sqrt(len(matrix)))
    return render_template('table.html', matrix=matrix,
                           current_group=Division.query.filter_by(id=group_id).first(), count=count)


@app.route('/groups/main')
def main_group():

    return render_template('groups.html', seasons=Database.select_seasons(), select=Database())


@app.route('/games')
def view_games():
    return render_template('games.html', Database=Database)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/members')
def members():
    return render_template("/members.html", members=Database.select_users_stat())


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


