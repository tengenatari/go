from app import app, db
from app import Rule, User, Player, Group, Game, Season
app.app_context().push()

try:
    db.create_all()
except:
    pass
