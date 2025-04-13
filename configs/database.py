from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.engine.url import quote_plus
from sqlalchemy.pool import QueuePool
DB_HOST = "localhost"
DB_PORT = 13306
DB_NAME = "db_timesheet"
DB_USER = "admin"
DB_PASSWORD = quote_plus("P@ssw0rd")   URL encode the password if it contains special characters
Create the database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
Create the SQLAlchemy engine with connection pooling settings
engine = create_engine(
DATABASE_URL,
connect_args={"charset": "utf8mb4"},
pool_pre_ping=True,
poolclass=QueuePool,
pool_size=10,   Adjust pool size based on expected load
max_overflow=20,   Allow some overflow connections
pool_timeout=30   Timeout for getting a connection from the pool
)
Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base class for our models
Base = declarative_base()
Existing Customer model
class Customer(Base):
__tablename__ = 'customers'
id = Column(Integer, primary_key=True, index=True)
name = Column(String, index=True)
Add any other fields relevant to the Customer model
New Project model
class Project(Base):
__tablename__ = 'projects'
id = Column(Integer, primary_key=True, index=True)
name = Column(String, index=True)
customer_id = Column(Integer, ForeignKey('customers.id'))
customer = relationship("Customer", back_populates="projects")
Establishing the relationship in the Customer model
Customer.projects = relationship("Project", order_by=Project.id, back_populates="customer")
Dependency to get the database session
def get_db():
db = SessionLocal()
try:
yield db
finally:
db.close()
Ensure the tables are created
Base.metadata.create_all(bind=engine)