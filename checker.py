from flask import flash
from models import Rule, User, Player, Group, Game, Season

def check_on_repeat(table, column, value, text):
    if table.query.filter(column == value).count() > 0:
        flash(text, category='error-msg')
        return True
    return False


def check_password(password, password_2):
    if len(password) < 7:
        flash("Пароль должен быть не менее 8 символов", category='error-msg')
        return False
    elif password != password_2:
        flash(message="Пароли не совпадают", category='error-msg')
        return False

    return True


def check_username(username):
    text = 'Пользователь с таким именем уже зарегистрирован'
    if len(username) < 4:
        flash("Имя пользователя должно быть не менее 5 символов", category='error-msg')
        return False
    elif len(username) >= 15:
        flash("Имя пользователя должно быть не более 15 символов", category='error-msg')
        return False
    elif check_on_repeat(User.name, username, text=text):
        return False
    return True


def check_email(email):
    text = 'Пользователь с такой почтой уже зарегистрирован'
    if email.split("@")[1] != 'study.utmn.ru' and email.split("@")[1] != 'utmn.ru':
        flash(message="Неверный формат почты, домен должен быть в формате utmn.ru", category='error-msg')
        return False
    elif check_on_repeat(User.email, email, text=text):
        return False
    return True


def check_form(username, email, password, password_2):

    if check_password(password, password_2) and check_email(email) and check_username(username):
        return True
    return False
