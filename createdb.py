from app import app, db
from app import Rule, User, Player, Group, Game, Season
from sqlalchemy import text
from UserLogin import UserLogin
app.app_context().push()

rule = Rule(name = 'test')
db.session.add(rule)
db.session.commit()