from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

"""
This file handles creatnig the actual connection to the database.

We will use sqlite3 database in development, but postgres in production.
Therefore we use config.py to get the database URL from .env
"""

# when using sqlite3 'check_same_thread' is set to False 
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args
)

# factory for sessions. Each request gets its own database sesssion
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()