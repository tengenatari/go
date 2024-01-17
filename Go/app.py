from datetime import datetime

from flask import Flask, render_template, request, flash

from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

app.config['SECRET_KEY'] = 'c3b9f846dc80fec3c879218547d1c93843bf1140c5c99e8812550819509fa78fc41d93799fe12370'



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/groups')
def groups():
    return render_template('groups.html')


@app.route('/members')
def members():
    return render_template("/members.html")


@app.route('/table.html')
def tables():
    return render_template("table.html")


@app.route('/authpage')
def authorization():
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

            player = Player(name=name, password=password, email=email)

            db.session.add(player)
            db.session.commit()

    return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)
