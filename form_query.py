from models import *
from main_request import Database
from flask import flash
from flask_login import current_user


def check_number(num):

    if all([nums.isdigit() for nums in num]):
        return True
    flash(message="Что-то пошло не так", category="error-msg")
    return False


def check_user(user_id, game_id):
    users = Database.select_users_in_game(game_id)
    if user_id == users[0][0] or user_id == users[1][0]:
        return True
    flash(message='Вы не можете отправить результат игры, участником которой не являетесь', category='error-msg')
    return False

def form_one(req):

    game_id = req["game_id"]
    if not(check_number(game_id)):
        flash(message="Что-то пошло не так", category="error-msg")
        return False
    if req["accept"] == "Принять":
        Database.update_obj(Game, Game.id, game_id, Game.is_accepted, True)
        return True
    elif req["accept"] == "Отклонить" or req["accept"] == "Отменить":
        Database.delete_obj(Game, Game.id, game_id)
        return True

    return False


def form_all(req):
    game_id = req["game_id"]
    if not(check_number(game_id)):
        flash(message="Что-то пошло не так", category="error-msg")
        return False
    if req['accept-all'] == "Принять все":
        Database.update_all_game_requests_to_you(current_user.get_user().id)
        return True
    elif req['accept-all'] == "Отклонить все":
        Database.delete_all_game_requests_to_you(current_user.get_user().id)
        return True

    flash("Что-то пошло не так", "error-msg")
    return False


def form_update(req):
    game_id = req["game_id"]
    if not(check_number(game_id)):
        flash(message="Что-то пошло не так", category="error-msg")
        return False
    if not(check_user(current_user.get_user().id, game_id)):
        return False
    print(req)
    if req['accept'] != "None":

        Database.delete_obj(Game, Game.id, game_id)
        return True
    elif req['accept-first'] != "None":

        Database.update_obj(Game, Game.id, game_id, Game.result, True)
        print(game_id)
        return True

    elif req['accept-second'] != "None":

        Database.update_obj(Game, Game.id, game_id, Game.result, False)
        return True

    flash(message="Что-то пошло не та1к", category="error-msg")
    return False


def select_form(req, query):

    if query == "one":
        return form_one(req)
    elif query == "all":
        return form_all(req)
    elif query == "update":
        return form_update(req)

    return False


