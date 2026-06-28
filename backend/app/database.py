# database.py
# Sets up the database connection and session management.


import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables so we can read the DATABASE_URL
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency injection function for FastAPI.
    Provides a database session to each route handler and ensures
    it is closed properly after the request completes, even if
    an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()