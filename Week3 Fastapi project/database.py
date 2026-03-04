from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

database_url = "postgresql://postgres:777189573@localhost:5432/A1Database"
engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



