from app import app, db
from app import Rule, User, Player, Group, Game, Season
from sqlalchemy import text

app.app_context().push()

try:
    db.create_all()
except:
    pass
res = db.session.execute(text('SELECT * FROM user'))

print(db.session.query(User).filter(User.id == '1').first())