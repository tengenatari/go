from app import app, db
from app import Rule, User, Player, Group, Game, Season
from sqlalchemy import func, case, desc
from sqlalchemy.sql.functions import coalesce
#from sqlalchemy import delete
from UserLogin import UserLogin

# --------------- #
# Select requests #
# --------------- #
    
def select_active_season():
    # Возвращает текущий сезон
    return db.session.query(Season).filter(Season.is_active == True).first()
    
def select_seasons():
    # Возвращает список всех существующих сезонов
    return db.session.query(Season).all()

def select_active_groups():
    # Возвращает список групп в текущем сезоне
    return db.session.query(Group).join(Season, (Group.season == Season.id) 
                                        & Season.is_active,
                                        isouter = False).all()

def select_groups_in_season(season_id: int):
    # Возвращает список групп в заданном сезоне
    return db.session.query(Group).filter(Group.season == season_id).all()

def select_users_data(max_games_value=10) -> list:
    
    # [0]: User_id
    # [1]: User_name
    # [2]: Player_id
    # [3]: Group_id
    # [4]: Group_name
    # [5]: Количество игр в текущем сезоне
    # [6]: Победы в текущем сезоне
    # [6]: Коэффициент побед в текущем сезоне Decimal('0E-10') или например Decimal('0.1000000000')

    return db.session.query(User.id,
                            User.name,
                            Player.c.id,
                            Group.id,
                            Group.name,
                            func.count(Game.id), 
                            func.sum(case(
                                (Game.result == (Game.first_player == Player.c.id), 1),
                                else_ = 0)),   
                            func.sum(case(
                                (Game.result == (Game.first_player == Player.c.id), 1),
                                else_ = 0)) / func.max(func.count(Game.id), max_games_value)
                            ).join(Player, 
                                   (Player.c.user == User.id)
                                   & User.is_valid,
                                   isouter = False 
                            ).join(Group,
                                   Group.id == Player.c.group,
                                   isouter = False
                            ).join(Season,
                                   (Season.id == Group.season)
                                   & Season.is_active,
                                   isouter = False
                            ).join(Game,
                                   (Game.first_player == Player.c.id)
                                   | (Game.second_player == Player.c.id),
                                   isouter = True        
                            ).group_by(
                                User.id,
                                User.name,
                                Player.c.id,
                                Group.id,
                                Group.name
                            ).order_by(
                                desc(
                                    func.sum(case(
                                    (Game.result == (Game.first_player == Player.c.id), 1),
                                    else_ = 0)) / func.max(func.count(Game.id), max_games_value)
                                )
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
        is_accepted   = True,
        result        = False,
        first_player  = 17,
        second_player = 20
    )
    db.session.add(g)

    db.session.commit()

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


