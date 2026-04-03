import os
from sqlmodel import create_engine , SQLModel , Session

from dotenv import load_dotenv

DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./database.db"
    print("⚠️ DATABASE_URL not set, falling back to SQLite")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
  SQLModel.metadata.create_all(engine)


def get_session():

  with Session(engine) as session:
    yield session