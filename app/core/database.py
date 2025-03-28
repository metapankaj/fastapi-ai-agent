import os
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

#database url validation
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in environment variables")

# Create database engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session factory for database interactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db():
    """
    Provide a database session for dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
