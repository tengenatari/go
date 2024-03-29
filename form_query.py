from models import *
from main_request import Database
from flask import flash, jsonify, render_template
from flask_login import current_user
from app import *


def check_number(num):

    if all([nums.isdigit() for nums in num]):
        return True
    return False


def check_user(user_id, game_id):
    users = Database.select_users_in_game(game_id)
    print(users)
    if user_id == users[0][0] or user_id == users[1][0]:
        return True
    return False


def form_all(req):
    if req['accept-all'] == "Принять все":
        Database.update_all_game_requests_to_you(current_user.get_user().id)
        return jsonify({'success': True})
    elif req['accept-all'] == "Отклонить все":
        Database.delete_all_game_requests_to_you(current_user.get_user().id)
        return jsonify({'success': True})
    message = 'Партии можно либо отклонить, либо принять'

    return jsonify({'success': False, 'message': message, 'id': 'error-msg-1'})


def form_update(req):
    game_id = req["game_id"]

    if (req["winner"] == '1') or (req["winner"] == '0'):

        Database.update_obj(Game, Game.id, game_id, Game.result, bool(int(req["winner"])))
        return jsonify({'success': True})
    message = 'Партия может быть только выигранной или проигранной'
    return jsonify({'success': False, 'message': message, 'id': 'error-msg-2'})


def form_delete(req):
    game_id = req['game_id']
    Database.delete_obj(Game, Game.id, game_id)
    return jsonify({'success': True})


def form_accept(req):
    game_id = req['game_id']
    users = Database.select_users_in_game(game_id)
    user_one = User.query.filter(User.id == users[0][0]).first().name
    user_two = User.query.filter(User.id == users[1][0]).first().name
    Database.update_obj(Game, Game.id, game_id, Game.is_accepted, True)
    return jsonify({'success': True, 'game_id': game_id,'page': render_template('accept.html', user_one=user_one,
                                                                                user_two=user_two, game_id=game_id)})


def select_form(req, query):
    message = 'Возникла непредвиденная ошибка'
    if query == "all":
        return form_all(req)

    if not (check_number(req['game_id'])):
        message = 'Неправильный формат данных'
        return jsonify({'success': False, 'message': message, 'id': 'error-msg-3'})

    if not (check_user(current_user.get_user().id, req['game_id'])):
        message = 'Вы не можете отправлять запросы на чужие партии'
        return jsonify({'success': False, 'message': message, 'id': 'error-msg-4'})

    if query == "delete":
        return form_delete(req)

    elif query == "update":
        return form_update(req)

    elif query == "accept":
        return form_accept(req)
    return jsonify({'success': False, 'message': message, 'id': 'error-msg-5'})


