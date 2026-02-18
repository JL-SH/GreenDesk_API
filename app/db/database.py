import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("DB_USER", "admin")
password = os.getenv("DB_PASSWORD", "admin123")
host = os.getenv("DB_HOST", "db")
port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "greendesk_db")

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

print(f"--- DATABASE CONNECTING TO: {host}:{port} AS {user} ---")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
