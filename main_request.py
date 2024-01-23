
from sqlalchemy import func, case, desc
from sqlalchemy.sql.functions import coalesce
from sqlalchemy import func, case, literal_column
#from sqlalchemy import delete
from UserLogin import UserLogin

def select_active_season(db, Rule, User, Player, Group, Game, Season):
    # Возвращает текущий сезон
    return db.session.query(Season).filter(Season.is_active == True).first()


def select_seasons(db, Rule, User, Player, Group, Game, Season):
    # Возвращает список всех существующих сезонов
    return db.session.query(Season).all()


def select_active_groups(db, Rule, User, Game, Player, Season, Group):
    # Возвращает список групп в текущем сезоне
    return db.session.query(Group).join(Season, (Group.season == Season.id)
                                        & Season.is_active,
                                        isouter=False).all()


def select_groups_in_season(season_id: int, db, Rule, User, Player, Group, Game, Season):
    # Возвращает список групп в заданном сезоне
    return db.session.query(Group).filter(Group.season == season_id).all()


def select_users_data(db, Rule, User, Player, Group, Game, Season, max_games_value=10) -> list:
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
                                else_=0)),
                            func.sum(case(
                                (Game.result == (Game.first_player == Player.c.id), 1),
                                else_=0)) / func.max(func.count(Game.id), max_games_value)
                            ).join(Player,
                                   (Player.c.user == User.id)
                                   & User.is_valid,
                                   isouter=False
                                   ).join(Group,
                                          Group.id == Player.c.group,
                                          isouter=False
                                          ).join(Season,
                                                 (Season.id == Group.season)
                                                 & Season.is_active,
                                                 isouter=False
                                                 ).join(Game,
                                                        (Game.first_player == Player.c.id)
                                                        | (Game.second_player == Player.c.id),
                                                        isouter=True
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
                else_=0)) / func.max(func.count(Game.id), max_games_value)
        )
    ).all()



