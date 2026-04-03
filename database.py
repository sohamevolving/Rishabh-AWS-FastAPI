from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER', 'root')}:"
    f"{os.getenv('MYSQL_PASSWORD', 'secret')}@"
    f"{os.getenv('MYSQL_HOST', 'mysql')}:"        # 'mysql' = Docker service name
    f"{os.getenv('MYSQL_PORT', '3306')}/"
    f"{os.getenv('MYSQL_DATABASE', 'store_db')}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # reconnects if the MySQL container restarts
    pool_recycle=3600,        # recycle connections every 1 hour
    echo=False,               # set True to log SQL queries during debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a DB session and closes it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()