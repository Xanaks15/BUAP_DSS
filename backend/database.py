from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# SSD Database Connection
SSD_USER = os.getenv("SSD_USER", "root")
SSD_PASSWORD = os.getenv("SSD_PASSWORD", "cRUltTthzitfncdZCrMTwHAHjbrGMHQk")
SSD_HOST = os.getenv("SSD_HOST", "shinkansen.proxy.rlwy.net")
SSD_PORT = os.getenv("SSD_PORT", "57709")
SSD_DB = os.getenv("SSD_DB", "railway")

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{SSD_USER}:{SSD_PASSWORD}@{SSD_HOST}:{SSD_PORT}/{SSD_DB}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
