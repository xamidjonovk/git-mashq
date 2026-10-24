from sqlalchemy import text
from .database import make_engine

engine = make_engine()
with engine.connect() as connection:
    baza_nomi = connection.execute(text("SELECT current_database()")).scalar_one()
    print(baza_nomi)
engine.dispose()