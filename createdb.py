from app import app, db
from models import Rule, User, Player, Division, Game, Season
from sqlalchemy import text
from UserLogin import UserLogin
app.app_context().push()

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

        g = db.session.query(Division).all()

    u = db.session.query(User).all()
    if not u:
        n = 5
        for i in range(n):
            text = f"AbaCaba{i}"
            user = User(
                name=text,
                password=text,
                email=f"{text}@utmn.ru",
                is_valid=True
            )
            db.session.add(user)
        db.session.commit()
        u = db.session.query(User).all()

    for j in g:
        p = j.players.all()
        if not p:
            for i in u:
                j.players.add(i)
            db.session.commit()
            p = j.players.all()

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

    # g = Game(
    #     is_accepted   = True,
    #     result        = False,
    #     first_player  = 17,
    #     second_player = 20
    # )
    # db.session.add(g)

    db.session.commit()


def main():
    app.app_context().push()

    Insert_test_values()




if __name__ == "__main__":
    main()