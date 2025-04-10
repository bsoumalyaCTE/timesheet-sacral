from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import quote_plus

DB_HOST = "localhost"
DB_PORT = 13306
DB_NAME = "db_timesheet"
DB_USER = "admin"
DB_PASSWORD = quote_plus("P@ssw0rd")  # URL encode the password if it contains special characters

# Create the database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"charset": "utf8mb4"}, pool_pre_ping=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()