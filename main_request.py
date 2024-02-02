from app import app, db
from models import Rule, User, Player, Division, Game, Season
from sqlalchemy import func, case, desc, BinaryExpression
from sqlalchemy.sql.functions import coalesce
# from sqlalchemy.sql import table, column
from sqlalchemy.orm import aliased
from sqlalchemy import delete, MetaData, select, text
from UserLogin import UserLogin


class Database:

    @staticmethod
    def select_active_season():
        # Возвращает текущий сезон
        return db.session.query(Season).filter(Season.is_active == True).first()

    @staticmethod
    def select_seasons():
        # Возвращает список всех существующих сезонов
        return db.session.query(Season).order_by(desc(Season.start_date)).all()

    @staticmethod
    def select_active_divisions():
        # Возвращает список групп в текущем сезоне
        return db.session.query(Division).join(Season, (Division.season == Season.id)
                                               & Season.is_active,
                                               isouter=False).all()

    @staticmethod
    def select_divisions_in_season(season_id: int):
        # Возвращает список групп в заданном сезоне
        return db.session.query(Division).filter(Division.season == season_id).all()

    @staticmethod
    def select_users_stat(user_id=0, max_games_value=10):
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
                ON Game.is_accepted
                AND Game.result IS NOT NULL
                AND (Game.first_player = "Player".id OR Game.second_player = "Player".id) 
        """
        db.session.execute(text(request), {'user_id_param': user_id})

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
        db.session.execute(text("DROP TABLE all_stat"))
        return result

    @staticmethod
    def select_accepted_games(finished=True, user_id=0):
        # Возвращает список кортежей с партиями. Партии принятые, где оба игрока находятся в одной группе.
        # Если параметр user_id заполнен (!= 0), то информация выводится только по одному пользователю.
        # Параметр finished отвечает за то, требуется нам отобрать активные партии или завершённые.

        # [0]: Game_id
        # [1]: Game.result

        # [2]: Division_id
        # [3]: Division_name

        # [4]: first_player.id
        # [5]: first_user.id
        # [6]: first_user.name

        # [7]: second_player.id
        # [8]: second_user.id
        # [9]: second_user.name

        f_Player = aliased(Player)
        s_Player = aliased(Player)
        f_User = aliased(User)
        s_User = aliased(User)

        result = db.session.query(Game.id,
                                  Game.result,
                                  Division.id,
                                  Division.name,
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
                                                & (s_Player.c.division == f_Player.c.division),
                                                isouter=False
                                                ).join(f_User,
                                                       f_User.id == f_Player.c.user,
                                                       isouter=False
                                                       ).join(s_User,
                                                              (s_User.id == s_Player.c.user)
                                                              & (True if user_id == 0 else ((f_User.id == user_id) | (
                                                                      s_User.id == user_id))),
                                                              isouter=False
                                                              ).join(Division,
                                                                     Division.id == f_Player.c.division,
                                                                     isouter=False
                                                                     ).filter(
            finished == (Game.result != None)
        )

        return result.all()

    @staticmethod
    def select_game_requests_to_you(user_id):
        # Возвращает список кортежей запросов на партию, которые нужно принять пользователю user_id.
        # Партии не принятые, где оба игрока находятся в одной группе.

        # [0]: Game_id
        # [1]: first_player.id
        # [2]: first_user.id
        # [3]: first_user.name

        request = """
        SELECT 
            game.id AS game_id, 
            game.first_player,
            f_user.id,
            f_user.name
        FROM game 
            INNER JOIN player AS s_player 
                ON (s_player.id = game.second_player)
                AND s_player.user = :user_param
                AND NOT game.is_accepted
            INNER JOIN player AS f_player 
                ON (f_player.id = game.first_player)
            INNER JOIN user AS f_user 
                ON f_user.id = f_player.user 
        """
        result = db.session.execute(text(request), {'user_param': user_id})
        return result.all()

    @staticmethod
    def select_your_game_requests(user_id):
        # Возвращает список кортежей запросов на партию, которые отправил user_id.
        # Партии не принятые, где оба игрока находятся в одной группе.

        # [0]: Game_id
        # [1]: second_player.id
        # [2]: second_user.id
        # [3]: second_user.name

        request = """
        SELECT 
            game.id AS game_id, 
            game.second_player,
            s_user.id,
            s_user.name
        FROM game 
            INNER JOIN player AS f_player 
                ON (f_player.id = game.first_player)
                AND f_player.user = :user_param
                AND NOT game.is_accepted
            INNER JOIN player AS s_player 
                ON (s_player.id = game.second_player)
            INNER JOIN user AS s_user 
                ON s_user.id = s_player.user 
        """
        result = db.session.execute(text(request), {'user_param': user_id})
        return result.all()

    @staticmethod
    def select_division_stat(division_id, max_games_value=10):
        # Возвращает список кортежей со статистикой по парам игроков в дивизионе.
        # При подсчёте учитываются только принятые и завершённые игры в данном дивизионе.
        # При формировании пар, пара игрока с самим собой не формируются.

        # [0]: style - строка, описывающая стиль отображения ячейки таблицы

        # [1]: left_user_id   - id пользователя, который стоит в строке таблицы дивизиона
        # [2]: left_user_name - Имя пользователя, который стоит в строке таблицы дивизиона

        # [3]: up_user_id   - id пользователя, который стоит в колонке таблицы дивизиона
        # [4]: up_user_name - Имя пользователя, который стоит в колонке таблицы дивизиона

        # [5]: pairs_games_lose - количеcтво поражений left_user от up_user
        # [6]: pairs_games_win   - количеcтво побед left_user над up_user

        # [7]: games_lose  - количеcтво поражений left_user в дивизионе
        # [8]: games_win   - количеcтво побед left_user в дивизионе
        # [9]: win_rate    - процент побед left_user в дивизионе
        # [10]: score       - рейтинг left_user в дивизионе

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
        db.session.execute(text(request), {'division_param': division_id})

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
            CASE 
                WHEN  pairs_stat.left_user_id = pairs_stat.up_user_id
                THEN :self_style
                ELSE :other_style 
            END AS style,
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
        parameters = {"self_style": "self-to-self",
                      "other_style": "self-to-other"}
        result = db.session.execute(text(request), parameters).all()

        db.session.execute(text("DROP TABLE games_stat"))
        db.session.execute(text("DROP TABLE pairs_stat"))
        db.session.execute(text("DROP TABLE user_stat"))

        return result

    @staticmethod
    def select_opponents(user_id):
        # Выводить по айди пользователя, игроков текущей группы (кроме самого себя).

        # [0]: user.name
        # [1]: player.id

        request = """
        SELECT 
            user.name, 
            player.id
        FROM user 
            INNER JOIN player 
                ON player.user = user.id
                AND user.id != :user_param
                AND player.division IN (
                    SELECT current_player.division
                    FROM player AS current_player
                        INNER JOIN division
                            ON division.id = current_player.division
                            AND current_player.user = :user_param
                        INNER JOIN season
                            ON season.id = division.season
                            AND season.is_active 
                ) 
        """
        result = db.session.execute(text(request), {'user_param': user_id})
        return result.all()

    @staticmethod
    def select_active_player(user_id):
        # Возвращает кортеж из одной ячейки - player.id активного пользователя для данного юзера

        request = """
            SELECT
                Player.id
            FROM User 
                INNER JOIN Player 
                    ON :user_param == User.id
                    AND Player.user = User.id 
                INNER JOIN Division 
                    ON Division.id = Player.division 
                INNER JOIN Season 
                    ON Season.id = Division.season 
                    AND Season.is_active
            LIMIT 1
            """
        result = db.session.execute(text(request), {'user_param': user_id})
        return result.first()

    @staticmethod
    def select_users_in_game(game_id):
        # Возвращает массив из кортежей user.id, которые учавствуют в партии game_id

        request = """
        SELECT
            user.id
        FROM user
            INNER JOIN player
                ON player.user = user.id
            INNER JOIN game
                ON game.id = :game_param
                AND player.id IN (game.first_player, game.second_player)
        """
        result = db.session.execute(text(request), {"game_param": game_id})
        return result.all()

    @staticmethod
    def count_pair_games(first_player_id, second_player_id, without_result=False):
        # По айди двух игроков вывести количество партий
        # Если параметр without_result=True, то выводит количество партий без результата

        request = """
        SELECT
            COUNT(game.id)
        FROM game
            INNER JOIN player AS f_player
                ON f_player.id = :f_player_param
                AND f_player.id in (game.first_player, game.second_player)
            INNER JOIN player AS s_player
                ON s_player.id = :s_player_param
                AND s_player.id in (game.first_player, game.second_player)
        WHERE
            TRUE IN (game.result IS NULL, NOT :result_param)
        """
        result = db.session.execute(text(request), {"f_player_param": first_player_id,
                                                    "s_player_param": second_player_id,
                                                    "result_param": without_result})
        return result.first()

    @staticmethod
    def create_game_request(f_Player_id, s_Player_id):
        # Запрос который по айди игроков, создаст партию, если они в одной группе, при успехе выдаст True, при ошибке False
        request = """
            SELECT
                f_player.division = s_player.division, 
                f_player.division,
                s_player.division
            FROM player AS f_player
                INNER JOIN player AS s_player
                    ON f_player.id = :f_player_param
                    AND s_player.id = :s_player_param
        """
        result = db.session.execute(text(request), {'f_player_param': f_Player_id, 's_player_param': s_Player_id})
        result = bool(result.first()[0])
        if result:
            new_game = Game(
                is_accepted=False,
                result=None,
                first_player=f_Player_id,
                second_player=s_Player_id
            )
            db.session.add(new_game)
            db.session.commit()
        return result

    @staticmethod
    def update_obj(_class, filter_col, filter_value, update_col, update_value):
        # Устанавливает значения update_value в атрибут update_col
        # во все экземпляры класса _class, удовлетворяющих условию filter_col == filter_value

        db.session.query(_class).filter(filter_col == filter_value).update({update_col: update_value},
                                                                           synchronize_session=False)
        db.session.commit()

    @staticmethod
    def update_all_game_requests_to_you(user_id):
        # Принимает все запросы на партию, которые нужно принять пользователю user_id.

        request = """
        UPDATE game
        SET is_accepted = True
        WHERE game.id IN (SELECT 
                game.id
            FROM game 
                INNER JOIN player AS s_player 
                    ON (s_player.id = game.second_player)
                    AND s_player.user = :user_param
                    AND NOT game.is_accepted
                INNER JOIN player AS f_player 
                    ON (f_player.id = game.first_player)
                INNER JOIN user AS f_user 
                    ON f_user.id = f_player.user) 
        """
        db.session.execute(text(request), {'user_param': user_id})
        db.session.commit()

    @staticmethod
    def add_user_in_the_last_division(user):
        # Добавлять пользователя в текущую группу B
        # user - эксемпляр класса User

        the_last_div = db.session.query(Division).join(Season).filter(Season.is_active).order_by(
            desc(Division.id)).limit(1).first()
        the_last_div.players.add(user)
        db.session.commit()

    @staticmethod
    def delete_obj(_class, filter_col, filter_value):
        # Удаляет все экземпляры класса _class, в которых filter_col == filter_value

        db.session.query(_class).filter(filter_col == filter_value).delete()
        db.session.commit()

    @staticmethod
    def delete_all_game_requests_to_you(user_id):
        # Отклоняет все запросы на партию, которые нужно принять пользователю user_id.

        request = """
        DELETE FROM game
        WHERE game.id IN (SELECT 
                game.id
            FROM game 
                INNER JOIN player AS s_player 
                    ON (s_player.id = game.second_player)
                    AND s_player.user = :user_param
                    AND NOT game.is_accepted
                INNER JOIN player AS f_player 
                    ON (f_player.id = game.first_player)
                INNER JOIN user AS f_user 
                    ON f_user.id = f_player.user) 
        """
        db.session.execute(text(request), {'user_param': user_id})
        db.session.commit()

    @staticmethod
    def create_new_season(new_season_name, division_data, max_games_value=10, switch_num=1):
        # процесс создания сезона:
        # 1) Создаётся выборка count_players_in_old_div[ ] - количество игроков в старых дивизионов
        # 2) Удаляются все партии, где game.result == None
        # 3) Создаётся выборка пользователей ladder_of_users[ ]. Выборка сортируется по текущему дивизиону, внутри дивизиона по очкам
        # 4) Cтарый сезон помечается season.is_active = false
        # 5) Создаётся новый сезон с именем name, n дивизионами, k[0 <= i < n] количеством участников дивизионов и именами дивизионов
        #    Двизионы создаются в порядке убывания престижа. (Иными словами первый создаётся дивизион S)
        # 6) Если old_k[i] - k[i] == 0, то первые j человек на стыке дивизионов меняются местами. Производим перестановку для каждого стыка дивизионов.
        # 7) В дивизион d[i] берутся первые k[i] человек из выборки ladder_of_users.

        # Пример входных данных:
        #     season_name = "Весна 2024"
        #     division_data = [
        #         ("new new S", 5),
        #         ("new new A", 5),
        #         ("new new B", 5)
        #     ]
        #     create_new_season(season_name, division_data)

        try:
            # 1:
            request = """
                SELECT
                    COUNT(player.id)
                FROM division
                    INNER JOIN season
                        ON season.id = division.season
                        AND season.is_active
                    INNER JOIN player
                        ON player.division = division.id
                GROUP BY
                    division.id
                ORDER BY
                    division.id
                """
            result = db.session.execute(text(request))
            count_players_in_old_div = [i[0] for i in result.all()]

            current_num = sum([i[1] for i in division_data])
            old_num = sum(count_players_in_old_div)
            if current_num != old_num:
                ex = f"Invalid number of players in new divisions. Curret: {current_num}. Old: {old_num}."
                print(ex)
                return ex
            
            # 2:
            request = """
                DELETE FROM game
                WHERE game.result IS NULL
                """
            db.session.execute(text(request))

            # 3:
            request = """
                SELECT
                    player.user,
                    SUM(IFNULL((game.result = (game.first_player = player.id)), FALSE)
                        )/(MAX(COUNT(game.id), :max_games_value) + 0.0) * 100 AS score
                FROM player
                    INNER JOIN division
                        ON player.division = division.id
                    INNER JOIN season
                        ON season.id = division.season
                        AND season.is_active
                    LEFT JOIN game
                        ON player.id IN (game.first_player, game.second_player)
                GROUP BY
                    player.id
                ORDER BY
                    division.id,
                    score DESC
                """
            result = db.session.execute(text(request), {"max_games_value": max_games_value})
            ladder_of_users = [i[0] for i in result.all()]

            # 4:
            db.session.query(Season).filter(Season.is_active).update({Season.is_active: False},
                                                                                synchronize_session=False)

            # 5:
            new_season = Season(
                name = new_season_name
            )
            db.session.add(new_season)

            divs = []
            for d in division_data:
                div = Division(name = d[0], season=new_season.id)
                divs.append(div)
                db.session.add(div)

            # 6:
            n = min(len(count_players_in_old_div), len(division_data)) - 1
            summ = -1

            for i in range(n):
                summ += count_players_in_old_div[i]
                if count_players_in_old_div[i] == division_data[i][1]:
                    for j in range(0, switch_num):
                        ladder_of_users[summ - j], ladder_of_users[summ + j + 1] = ladder_of_users[summ + j + 1], ladder_of_users[summ - j]

            # 7:
            for d in range(len(division_data)):
                div = divs[d]
                for i in range(division_data[d][1]):
                    user_id = ladder_of_users.pop(0)
                    user = db.session.query(User).filter(User.id == user_id).first()
                    div.players.add(user)

            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
