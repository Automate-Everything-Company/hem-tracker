from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.src.core.config import USER, PASSWORD, HOST, DB

DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
