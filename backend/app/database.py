import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

USER = os.getenv("MYSQL_USER")
PASSWORD = os.getenv("MYSQL_PASSWORD")
HOST = os.getenv("MYSQL_HOST")
DB = os.getenv("MYSQL_DB")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

