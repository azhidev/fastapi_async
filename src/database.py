from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import dotenv, os
dotenv.load_dotenv(os.path.join('.env'))
Base = declarative_base()
engine = create_engine(os.environ.get("MY_SQL_ADDRESS"), echo = True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()