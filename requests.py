from app import app, db
from models import Rule, User, Player, Division, Game, Season
from sqlalchemy import func, case, desc, BinaryExpression
from sqlalchemy.sql.functions import coalesce
#from sqlalchemy.sql import table, column
from sqlalchemy.orm import aliased
from sqlalchemy import delete, MetaData, select, text
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

def select_active_divisions():
    # Возвращает список групп в текущем сезоне
    return db.session.query(Division).join(Season, (Division.season == Season.id) 
                                        & Season.is_active,
                                        isouter = False).all()

def select_divisions_in_season(season_id: int):
    # Возвращает список групп в заданном сезоне
    return db.session.query(Division).filter(Division.season == season_id).all()

def select_users_stat(max_games_value=10, user_id=0):
    # Выдаёт список кортежей со статистикой по активным пользователям. 
    # Если параметр user_id заполнен (!= 0), то информация выводится только по одному пользователю.

    # [0]: User_id
    # [1]: User_name
    # [2]: division_id
    # [3]: division_name

    # [5]: all_win  - общее количество побед
    # [6]: all_lose - общее количество поражений

    # [7]: division_win  - количество побед в текущем сезоне
    # [8]: division_lose - количество поражений в текущем сезоне
    # [9]: score         - рейтинг в текущем сезоне
    
    request = """
    CREATE TEMP TABLE user_data AS
    SELECT 
        User.id AS user_id, 
        User.name AS user_name, 
        "Division".id AS division_id, 
        "Division".name AS division_name, 
        Season.is_active AS season_is_active,
        Game.id AS game_id, 
        IFNULL(Game.result = (Game.first_player = "Player".id), FALSE) AS win
    FROM User 
        INNER JOIN Player 
            ON :user_id_param IN (0, User.id)
            AND Player.user = User.id 
            AND User.is_valid
        INNER JOIN "Division" 
            ON "Division".id = Player."division" 
        INNER JOIN Season 
            ON Season.id = "Division".season 
        LEFT OUTER JOIN game 
            ON Game.is_accepted = 1 
            AND (Game.first_player = "Player".id OR Game.second_player = "Player".id) 
    """
    db.session.execute(text(request), {'user_id_param':user_id})

    request = """
    CREATE TEMP TABLE division_stat AS
    SELECT 
        user_data.user_id AS user_id, 
        user_data.user_name AS user_name,
        user_data.division_id AS division_id, 
        user_data.division_name AS division_name, 
        COUNT(user_data.game_id) AS games_count, 
        SUM(user_data.win) AS games_win,
        SUM(user_data.win)/(MAX(COUNT(user_data.game_id), :max_games_value) + 0.0) * 100 AS score
    FROM user_data
    WHERE user_data.season_is_active
    GROUP BY 
        user_data.user_id,
        user_data.user_name,
        user_data.division_id, 
        user_data.division_name
    """
    db.session.execute(text(request), {"max_games_value": max_games_value})

    request = """
    CREATE TEMP TABLE all_stat AS
    SELECT 
        user_data.user_id AS user_id, 
        COUNT(user_data.game_id) AS games_count, 
        SUM(user_data.win) AS games_win,
        SUM(user_data.win)/(MAX(COUNT(user_data.game_id), :max_games_value) + 0.0) * 100 AS score
    FROM user_data
    GROUP BY 
        user_data.user_id 
    """
    db.session.execute(text(request), {"max_games_value": max_games_value})

    request = """
    SELECT 
        division_stat.user_id, 
        division_stat.user_name,
        division_stat.division_id, 
        division_stat.division_name, 
        all_stat.games_win AS all_win,
        all_stat.games_count - all_stat.games_win AS all_lose,
        division_stat.games_win AS division_win,
        division_stat.games_count - division_stat.games_win AS division_lose,
        division_stat.score
    FROM division_stat
        INNER JOIN all_stat
            ON all_stat.user_id = division_stat.user_id
    ORDER BY
        division_stat.score DESC
    """

    result = db.session.execute(text(request), {}).all()

    db.session.execute(text("DROP TABLE user_data"))
    db.session.execute(text("DROP TABLE division_stat"))
    return result


def select_accepted_games(finished=True, user_id=0):
    # Возвращает список кортежей с партиями. Партии принятые, где оба игрока находятся в одной группе.
    # Если параметр user_id заполнен (!= 0), то информация выводится только по одному пользователю.
    # Если параметр finished отвечает за то, требуется нам отобрать активные партии или завершённые.

    # [0]: Game_id 
    # [1]: Division_id
    # [2]: Game.result 
    
    # [3]: first_player.id
    # [4]: first_user.id
    # [5]: first_user.name

    # [6]: second_player.id
    # [7]: second_user.id
    # [8]: second_user.name

    f_Player = aliased(Player) 
    s_Player = aliased(Player) 
    f_User   = aliased(User) 
    s_User   = aliased(User) 

    return db.session.query(Game.id, 
                            f_Player.c.division,
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
                                   isouter = False     
                            ).join(s_Player, 
                                   (s_Player.c.id == Game.second_player)
                                   & (s_Player.c.division == f_Player.c.division),
                                   isouter = False     
                            ).join(f_User,
                                   f_User.id == f_Player.c.user,
                                   isouter = False
                            ).join(s_User,
                                   (s_User.id == s_Player.c.user)
                                   & (True if user_id == 0 else ((f_User.id == user_id)|(s_User.id == user_id))),
                                   isouter = False
                            ).filter(
                                finished == (Game.result is not None)    
                            ).all()

def select_game_requests_to_you(user_id):
    # Возвращает список кортежей запросов на партию, которые нужно принять пользователю user_id.
    # Партии не принятые, где оба игрока находятся в одной группе. 

    # [0]: Game_id 
    # [1]: Division_id
    # [2]: first_player.id
    # [3]: first_user.id
    # [4]: first_user.name

    f_Player = aliased(Player) 
    s_Player = aliased(Player) 
    f_User   = aliased(User) 

    return db.session.query(Game.id, 
                            f_Player.c.division,
                            Game.first_player,
                            f_User.id,
                            f_User.name,                      
                            ).join(f_Player, 
                                   (f_Player.c.id == Game.first_player)
                                   & (not Game.is_accepted),
                                   isouter = False     
                            ).join(s_Player, 
                                   (s_Player.c.id == Game.second_player)
                                   & (s_Player.c.division == f_Player.c.division)
                                   & (s_Player.c.user == user_id),
                                   isouter = False 
                            ).join(f_User,
                                   f_User.id == f_Player.c.user,
                                   isouter = False
                            ).all()

def select_your_game_requests(user_id):
    # Возвращает список кортежей запросов на партию, которые отправил user_id.
    # Партии не принятые, где оба игрока находятся в одной группе. 

    # [0]: Game_id 
    # [1]: Division_id
    # [2]: second_player.id
    # [3]: second_user.id
    # [4]: second_user.name

    f_Player = aliased(Player) 
    s_Player = aliased(Player) 
    s_User   = aliased(User) 

    return db.session.query(Game.id, 
                            s_Player.c.division,
                            Game.second_player,
                            s_User.id,
                            s_User.name,                      
                            ).join(f_Player, 
                                   (f_Player.c.id == Game.first_player)
                                   & (not Game.is_accepted)
                                   & (f_Player.c.user == user_id),
                                   isouter = False     
                            ).join(s_Player, 
                                   (s_Player.c.id == Game.second_player)
                                   & (s_Player.c.division == f_Player.c.division),
                                   isouter = False 
                            ).join(s_User,
                                   s_User.id == s_Player.c.user,
                                   isouter = False
                            ).all()

def select_division_stat(division_id, max_games_value=10):
    # Возвращает список кортежей со статистикой по парам игроков в дивизионе.
    # При подсчёте учитываются только принятые и завершённые игры в данном дивизионе.
    # При формировании пар, пара игрока с самим собой не формируются.

    # [0]: left_user_id   - id пользователя, который стоит в строке таблицы дивизиона
    # [1]: left_user_name - Имя пользователя, который стоит в строке таблицы дивизиона

    # [2]: up_user_id   - id пользователя, который стоит в колонке таблицы дивизиона
    # [3]: up_user_name - Имя пользователя, который стоит в колонке таблицы дивизиона

    # [4]: pairs_games_lose - количеcтво поражений left_user от up_user
    # [5]: pairs_games_win   - количеcтво побед left_user над up_user

    # [6]: games_lose  - количеcтво поражений left_user в дивизионе
    # [7]: games_win   - количеcтво побед left_user в дивизионе
    # [8]: win_rate    - процент побед left_user в дивизионе
    # [9]: score       - рейтинг left_user в дивизионе
    
    request = """
    CREATE TEMP TABLE games_stat AS
    SELECT 
        left_user.id AS left_user_id, 
        left_user.name AS left_user_name, 
        up_user.id AS up_user_id, 
        up_user.name AS up_user_name, 
        game.id AS game_id, 
        IFNULL((game.result = (game.first_player = left_player.id)), FALSE) AS win 
    FROM user AS left_user 
        INNER JOIN Player AS left_player 
            ON (left_player.user = left_user.id) 
            AND (left_player."division" = :division_param) 
        INNER JOIN Player AS up_player 
            ON (up_player."division" = :division_param)
        INNER JOIN user AS up_user 
            ON up_user.id = up_player.user 
        LEFT OUTER JOIN game 
            ON game.is_accepted = TRUE
            AND game.result IS NOT NULL
            AND up_player.id IN (game.first_player, game.second_player)
            AND left_player.id IN (game.first_player, game.second_player)
            AND up_player.id != left_player.id
    """
    db.session.execute(text(request), {'division_param':division_id})

    request = """
    CREATE TEMP TABLE pairs_stat AS
    SELECT
        games_stat.left_user_id,
        games_stat.left_user_name,
        games_stat.up_user_id,
        games_stat.up_user_name,
        COUNT(games_stat.game_id) AS games_count,
        SUM(games_stat.win) AS games_win
    FROM games_stat
    GROUP BY
        games_stat.left_user_id,
        games_stat.left_user_name,
        games_stat.up_user_id,
        games_stat.up_user_name
    """
    db.session.execute(text(request))

    request = """
    CREATE TEMP TABLE user_stat AS
    SELECT
        games_stat.left_user_id,
        games_stat.left_user_name,
        COUNT(games_stat.game_id) AS games_count,
        SUM(games_stat.win) AS games_win,
        IFNULL(SUM(games_stat.win)/(COUNT(games_stat.game_id) + 0.0), 0.0) * 100 AS win_rate,
        SUM(games_stat.win)/(MAX(COUNT(games_stat.game_id), :max_games_value) + 0.0) * 100 AS score
    FROM games_stat
    GROUP BY
        games_stat.left_user_id,
        games_stat.left_user_name
    """
    db.session.execute(text(request), {"max_games_value": max_games_value})
    
    request = """
    SELECT
        pairs_stat.left_user_id,
        pairs_stat.left_user_name,
        pairs_stat.up_user_id,
        pairs_stat.up_user_name,
        pairs_stat.games_count - pairs_stat.games_win,
        pairs_stat.games_win,
        user_stat.games_count - user_stat.games_win,
        user_stat.games_win,
        user_stat.win_rate, 
        user_stat.score
    FROM pairs_stat
        INNER JOIN user_stat 
            ON user_stat.left_user_id = pairs_stat.left_user_id
    """
    result = db.session.execute(text(request)).all()            
    
    db.session.execute(text("DROP TABLE games_stat"))
    db.session.execute(text("DROP TABLE pairs_stat"))
    db.session.execute(text("DROP TABLE user_stat"))

    return result

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

    q = select_division_stat(4)
    for i in q:
       print(i)
    
if __name__ == "__main__":
    main()


