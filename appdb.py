from app import app, db
from app import Rule, User, Player, Group, Game, Season
from sqlalchemy import text
from sqlalchemy import delete
from UserLogin import UserLogin


app.app_context().push()

def create_players(users: list, g: Group):

    players = [Player(group = g, user = u) for u in users]
    db.session.add(players)
    db.session.commit()

def start_season(s_name: str):
    new_season = Season(
        name = s_name
    )
    db.session.add(new_season)
    db.session.commit()

def add_group(g_name: str):
    s = db.session.query(Season).filter(Season.is_active == True).first()
    new_group = Group(
        name = g_name,
        season = s.id
    )
    db.session.add(new_group)
    db.session.commit()
    
s = db.session.query(Season).all()
if not s:
    start_season("Cool season!")
    s = db.session.query(Season).all()

g = db.session.query(Group).first()
if not g:
    add_group("S")
    g = db.session.query(Group).first()

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

p = g.players.all()
if not p:
    for i in u:
        g.players.add(i)
    db.session.commit()
    p = g.players.all()





