from app import app, db
from models import Rule, User, Player, Division, Game, Season
from werkzeug.security import generate_password_hash

#from sqlalchemy import func, case, desc, BinaryExpression
#from sqlalchemy.sql.functions import coalesce
#from sqlalchemy.sql import table, column
#from sqlalchemy.orm import aliased
#from sqlalchemy import delete, MetaData, select, text
    
def Insert_test_values():
    db.drop_all()
    db.create_all()

    s = db.session.query(Season).all()
    if not s:
        
        old_season = Season(
            name = "Old season!",
            is_active = False
        )
        db.session.add(old_season)

        new_season = Season(
            name = "Cool season!"
        )
        db.session.add(new_season)
        db.session.commit()

        s = db.session.query(Season).all()

    g = db.session.query(Division).first()
    if not g:
        s = db.session.query(Season).filter(Season.is_active == False).first()
        new_division = Division(
            name = "Old S",
            season = s.id
        )
        db.session.add(new_division)
        new_division = Division(
            name = "Old A",
            season = s.id
        )
        db.session.add(new_division)
        new_division = Division(
            name = "Old B",
            season = s.id
        )
        db.session.add(new_division)

        s = db.session.query(Season).filter(Season.is_active == True).first()
        new_division = Division(
            name = "S",
            season = s.id
        )
        db.session.add(new_division)
        new_division = Division(
            name = "A",
            season = s.id
        )
        db.session.add(new_division)
        new_division = Division(
            name = "B",
            season = s.id
        )
        db.session.add(new_division)
        db.session.commit()

        g = db.session.query(Division).all()

    u = db.session.query(User).all()
    
    for d in g:
        n = 5
        for i in range(n):
            text = f"AbaCaba{i}_d{d.id}"
            user = User(
            name = text,
            password = generate_password_hash(text),
            email = f"{text}@utmn.ru",
            is_valid = True
            )
            db.session.add(user)
        db.session.commit()
        u = db.session.query(User).filter(User.name.like(f"%d{d.id}%")).all()
        for i in u:
            d.players.add(i)
        db.session.commit()
    
    g = Game(
        is_accepted   = True,
        result        = True,
        first_player  = 16,
        second_player = 17
    )
    db.session.add(g)

    g = Game(
        is_accepted   = True,
        result        = True,
        first_player  = 16,
        second_player = 17
    )
    db.session.add(g)

    g = Game(
        is_accepted   = True,
        result        = True,
        first_player  = 17,
        second_player = 16
    )
    db.session.add(g)

    g = Game(
        is_accepted   = True,
        result        = False,
        first_player  = 17,
        second_player = 16
    )
    db.session.add(g)
    
    g = Game(
        is_accepted   = True,
        result        = True,
        first_player  = 18,
        second_player = 17
    )
    db.session.add(g)

    g = Game(
        is_accepted   = True,
        result        = True,
        first_player  = 16,
        second_player = 19
    )
    db.session.add(g)

    g = Game(
        is_accepted   = False,
        result        = None,
        first_player  = 17,
        second_player = 20
    )
    db.session.add(g)

    g = Game(
        is_accepted   = False,
        result        = None,
        first_player  = 16,
        second_player = 17
    )
    db.session.add(g)

    g = Game(
        is_accepted   = False,
        result        = None,
        first_player  = 17,
        second_player = 16
    )
    db.session.add(g)

    g = Game(
        is_accepted   = False,
        result        = None,
        first_player  = 17,
        second_player = 16
    )
    db.session.add(g)

    g = Game(
        is_accepted   = False,
        result        = None,
        first_player  = 17,
        second_player = 16
    )
    db.session.add(g)

    g = Game(
        is_accepted   = True,
        result        = None,
        first_player  = 17,
        second_player = 16
    )
    db.session.add(g)

    db.session.commit()

def main():    
    app.app_context().push()
    
    Insert_test_values()

    q = db.session.query(User.id, User.name, Player.c.id, Player.c.division).join(Player).all()
    for i in q:
        print(i)

if __name__ == "__main__":
    main()


