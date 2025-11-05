from sqlalchemy import engine, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

DATABASE_URL = f"postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

    

