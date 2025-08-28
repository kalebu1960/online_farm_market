from .db import Base, engine, SessionLocal
from .models import Category
from sqlalchemy.exc import IntegrityError

def seed_categories():
    categories = ["Cattle", "Goats/Sheep", "Poultry", "Pigs", "Rabbits", "Animal Products"]
    db = SessionLocal()
    try:
        for name in categories:
            c = Category(name=name)
            db.add(c)
        db.commit()
    except IntegrityError:
        db.rollback()
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    seed_categories()
