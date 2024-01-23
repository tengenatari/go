
from sqlalchemy import func, case, desc, BinaryExpression
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql import bindparam
from sqlalchemy.orm import aliased
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


def select_accepted_games(db, Rule, User, Game, Player, Season, Group, finished=True, user_id=0):
    # Возвращает список кортежей с партиями. Партии принятые, где оба игрока находятся в одной группе.
    # Если параметр user_id заполнен (!= 0), то информация выводится только по одному пользователю.
    # Если параметр finished отвечает за то, требуется нам отобрать активные партии или завершённые.

    # [0]: Game_id
    # [1]: Group_id
    # [2]: Game.result

    # [3]: first_player.id
    # [4]: first_user.id
    # [5]: first_user.name

    # [6]: second_player.id
    # [7]: second_user.id
    # [8]: second_user.name

    f_Player = aliased(Player)
    s_Player = aliased(Player)
    f_User = aliased(User)
    s_User = aliased(User)

    return db.session.query(Game.id,
                            f_Player.c.group,
                            Game.result,
                            Game.first_player,
                            f_User.id,
                            f_User.name,
                            Game.second_player,
                            s_User.id,
                            s_User.name
                            ).join(f_Player,
                                   (f_Player.c.id == Game.first_player)
                                   & Game.is_accepted,
                                   isouter=False
                                   ).join(s_Player,
                                          (s_Player.c.id == Game.second_player)
                                          & (s_Player.c.group == f_Player.c.group),
                                          isouter=False
                                          ).join(f_User,
                                                 f_User.id == f_Player.c.user,
                                                 isouter=False
                                                 ).join(s_User,
                                                        (s_User.id == s_Player.c.user)
                                                        & (True if user_id == 0 else (
                                                                    (f_User.id == user_id) | (s_User.id == user_id))),
                                                        isouter=False
                                                        ).filter(
        finished == (Game.result is not None)
    ).all()


def select_game_requests_to_you(db, Rule, User, Game, Player, Season, Group, user_id):
    # Возвращает список кортежей запросов на партию, которые нужно принять пользователю user_id.
    # Партии не принятые, где оба игрока находятся в одной группе.

    # [0]: Game_id
    # [1]: Group_id
    # [2]: first_player.id
    # [3]: first_user.id
    # [4]: first_user.name

    f_Player = aliased(Player)
    s_Player = aliased(Player)
    f_User = aliased(User)

    return db.session.query(Game.id,
                            f_Player.c.group,
                            Game.first_player,
                            f_User.id,
                            f_User.name,
                            ).join(f_Player,
                                   (f_Player.c.id == Game.first_player)
                                   & (not Game.is_accepted),
                                   isouter=False
                                   ).join(s_Player,
                                          (s_Player.c.id == Game.second_player)
                                          & (s_Player.c.group == f_Player.c.group)
                                          & (s_Player.c.user == user_id),
                                          isouter=False
                                          ).join(f_User,
                                                 f_User.id == f_Player.c.user,
                                                 isouter=False
                                                 ).all()


def select_your_game_requests(db, Rule, User, Game, Player, Season, Group, user_id):
    # Возвращает список кортежей запросов на партию, которые отправил user_id.
    # Партии не принятые, где оба игрока находятся в одной группе.

    # [0]: Game_id
    # [1]: Group_id
    # [2]: second_player.id
    # [3]: second_user.id
    # [4]: second_user.name

    f_Player = aliased(Player)
    s_Player = aliased(Player)
    s_User = aliased(User)

    return db.session.query(Game.id,
                            s_Player.c.group,
                            Game.second_player,
                            s_User.id,
                            s_User.name,
                            ).join(f_Player,
                                   (f_Player.c.id == Game.first_player)
                                   & (not Game.is_accepted)
                                   & (f_Player.c.user == user_id),
                                   isouter=False
                                   ).join(s_Player,
                                          (s_Player.c.id == Game.second_player)
                                          & (s_Player.c.group == f_Player.c.group),
                                          isouter=False
                                          ).join(s_User,
                                                 s_User.id == s_Player.c.user,
                                                 isouter=False
                                                 ).all()
