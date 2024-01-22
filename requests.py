from app import app, db
from app import Rule, User, Player, Group, Game, Season
#from sqlalchemy import text
#from sqlalchemy import delete
from UserLogin import UserLogin

# --------------- #
# Select requests #
# --------------- #
    
def select_active_season() -> Season:
    return db.session.query(Season).filter(Season.is_active == True).first()
    
def select_active_groups() -> list:
    return db.session.query(Group).join(Season, (Group.season == Season.id) 
                                        & Season.is_active,
                                        isouter = False).all()

def select_users_data() -> list:
    # print(db.session.query(User.id,
    #                         User.name,
    #                         Player.c.id,
    #                         Group.id,
    #                         Group.name
    #                         ).join(Player, 
    #                                Player.c.user == User.id,
    #                                isouter = True 
    #                         ).join(Group,
    #                                Group.id == Player.c.group,
    #                                isouter = True
    #                         ).join(Season,
    #                                (Season.id == Group.season)
    #                                & Season.is_active
    #                                & User.is_valid,
    #                                isouter = False
    #                         ).join(Game,
    #                                (Game.first_player == Player.c.id)
    #                                | (Game.second_player == Player.c.id),
    #                                isouter = True
    #                         ))
    return db.session.query(User.id,
                            User.name,
                            Player.c.id,
                            Group.id,
                            Group.name,
                            Game.id
                            ).join(Player, 
                                   Player.c.user == User.id,
                                   isouter = True 
                            ).join(Group,
                                   Group.id == Player.c.group,
                                   isouter = True
                            ).join(Season,
                                   (Season.id == Group.season)
                                   & Season.is_active
                                   & User.is_valid,
                                   isouter = False
                            ).join(Game,
                                   (Game.first_player == Player.c.id)
                                   | (Game.second_player == Player.c.id),
                                   isouter = True
                            ).all()
# ------------------ #
# Insert test values #
# ------------------ #
    
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

    g = db.session.query(Group).first()
    if not g:
        s = db.session.query(Season).filter(Season.is_active == False).first()
        new_group = Group(
            name = "Old S",
            season = s.id
        )
        db.session.add(new_group)
        new_group = Group(
            name = "Old A",
            season = s.id
        )
        db.session.add(new_group)
        new_group = Group(
            name = "Old B",
            season = s.id
        )
        db.session.add(new_group)

        s = db.session.query(Season).filter(Season.is_active == True).first()
        new_group = Group(
            name = "S",
            season = s.id
        )
        db.session.add(new_group)
        new_group = Group(
            name = "A",
            season = s.id
        )
        db.session.add(new_group)
        new_group = Group(
            name = "B",
            season = s.id
        )
        db.session.add(new_group)
        db.session.commit()

        g = db.session.query(Group).all()

    u = db.session.query(User).all()
    if not u:
        n = 5
        for i in range(n):
            text = f"AbaCaba{i}"
            user = User(
            name = text,
            password = text,
            email = f"{text}@utmn.ru",
            is_valid = True
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

def main():    
    app.app_context().push()
    
    #Insert_test_values()

    # q = select_active_groups()
    # for i in q:
    #     print(i.name, i.season)

    q = select_users_data()
    for i in q:
       print(i)
    
if __name__ == "__main__":
    main()


