from math import sqrt
from flask import Flask, render_template, request, flash, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from checker import check_form
from main_request import *
from app import db, app, login_manager
from models import *
from typing import Callable
from functools import partial
from form_query import *


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


@app.route('/send-request', methods=['POST'])
@login_required
def send_request():

    req = request.form
    user2 = req["user2"]

    if Database.count_pair_games(Database.select_active_player(current_user.get_user().id)[0], user2,
                                 True)[0] >= 1:
        message = 'Вы не можете отправить более одного вызова одному игроку'
        return jsonify({'success': False, 'message': message, 'id': 'error-msg-6'})
    elif Database.count_pair_games(Database.select_active_player(current_user.get_user().id)[0], user2)[0] >= 4:
        message = 'Вы не можете сыграть более четырех партий с одним игрокком'
        return jsonify({'success': False, 'message': message, 'id': 'error-msg-7'})

    game_id = Database.create_game_request(Database.select_active_player(current_user.get_user().id)[0], user2)

    if (game_id):
        return jsonify({'success': True, 'page': render_template('game-block.html', opponent=req["opponent"], game_id=game_id),
                        'game_id': game_id})
    message = 'Возникла непредвиденная ошибка'
    return jsonify({'success': False, 'message': message, 'id': 'error-msg-8'})


@app.route('/profile/join/group', methods=['GET', 'POST'])
@login_required
def send_request_join_group():
    if request.method == 'POST':
        if current_user.get_user().is_valid:
            flash("Вы успешно вступили в группу", category='msg-success')
        else:
            flash("Вы не можете вступить в группу, пока не подтвердите почту", category='error-msg')
    return redirect('/profile')


@app.route('/update-game/<string:query>', methods=['POST'])
@login_required
def decline_game_request(query):
    req = request.form
    return select_form(req, query)


@app.route('/user/rules/admin-panel')
@login_required
def admin_panel():

    return render_template('admin-panel.html')


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


