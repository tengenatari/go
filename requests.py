from app import app, db
from models import Rule, User, Player, Division, Game, Season
from werkzeug.security import generate_password_hash

from main_request import *


# from sqlalchemy import func, case, desc, BinaryExpression
# from sqlalchemy.sql.functions import coalesce
# from sqlalchemy.sql import table, column
# from sqlalchemy.orm import aliased
# from sqlalchemy import delete, MetaData, select, text

def Insert_test_values():
    db.drop_all()
    db.create_all()

    s = db.session.query(Season).all()
    if not s:
        old_season = Season(
            name="Old season!",
            is_active=False
        )
        db.session.add(old_season)

        new_season = Season(
            name="Cool season!"
        )
        db.session.add(new_season)
        db.session.commit()

        s = db.session.query(Season).all()

    g = db.session.query(Division).first()
    if not g:
        s = db.session.query(Season).filter(Season.is_active == False).first()
        new_division = Division(
            name="Old S",
            season=s.id
        )
        db.session.add(new_division)
        new_division = Division(
            name="Old A",
            season=s.id
        )
        db.session.add(new_division)
        new_division = Division(
            name="Old B",
            season=s.id
        )
        db.session.add(new_division)

        s = db.session.query(Season).filter(Season.is_active == True).first()
        new_division = Division(
            name="S",
            season=s.id
        )
        db.session.add(new_division)
        new_division = Division(
            name="A",
            season=s.id
        )
        db.session.add(new_division)
        new_division = Division(
            name="B",
            season=s.id
        )
        db.session.add(new_division)
        db.session.commit()

    n = 5
    for i in range(3 * n):
        text = f"AbaCaba{i + 1}"
        user = User(
            name=text,
            password=generate_password_hash(text),
            email=f"{text}@utmn.ru",
            is_valid=True
        )
        db.session.add(user)
    db.session.commit()

    u = list(db.session.query(User).all())
    g = db.session.query(Division).join(Season).filter(Season.is_active == False).order_by(Division.id).all()

    for d in range(3):
        div = g[d]
        for i in range(n):
            div.players.add(u[i + d * n])
        db.session.commit()

    g = db.session.query(Division).join(Season).filter(Season.is_active).order_by(Division.id).all()

    for d in range(3):
        div = g[d]
        for i in range(n):
            div.players.add(u[i + d * n])
        db.session.commit()

    g = Game(
        is_accepted=True,
        result=True,
        first_player=16,
        second_player=17
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=16,
        second_player=17
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=17,
        second_player=16
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=False,
        first_player=17,
        second_player=16
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=18,
        second_player=17
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=16,
        second_player=19
    )
    db.session.add(g)

    g = Game(
        is_accepted=False,
        result=None,
        first_player=17,
        second_player=20
    )
    db.session.add(g)

    g = Game(
        is_accepted=False,
        result=None,
        first_player=16,
        second_player=17
    )
    db.session.add(g)

    g = Game(
        is_accepted=False,
        result=None,
        first_player=17,
        second_player=16
    )
    db.session.add(g)

    g = Game(
        is_accepted=False,
        result=None,
        first_player=17,
        second_player=16
    )
    db.session.add(g)

    g = Game(
        is_accepted=False,
        result=None,
        first_player=17,
        second_player=16
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=None,
        first_player=17,
        second_player=16
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=1,
        second_player=2
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=2,
        second_player=3
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=3,
        second_player=4
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=2,
        second_player=1
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=27,
        second_player=28
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=False,
        first_player=27,
        second_player=29
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=29,
        second_player=27
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=29,
        second_player=26
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=29,
        second_player=26
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=29,
        second_player=28
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=29,
        second_player=28
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=29,
        second_player=28
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=29,
        second_player=28
    )
    db.session.add(g)

    g = Game(
        is_accepted=True,
        result=True,
        first_player=29,
        second_player=30
    )
    db.session.add(g)

    db.session.commit()


def main():
    app.app_context().push()

    Insert_test_values()

    # q = db.session.query(Game.id, Game.first_player, Game.second_player, Game.result, Game.is_accepted).all()
    # for i in q:
    #     print(i)

    q = db.session.query(User.id, User.name, Player.c.id, Player.c.division).join(Player).all()
    for i in q:
        print(i)
    # print(q)


if __name__ == "__main__":
    main()