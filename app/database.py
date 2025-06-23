from sqlalchemy import Column, Integer, DateTime, String, create_engine, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASEURL = os.getenv("DATABASEURL")

# Create engine for database connection
engine = create_engine(DATABASEURL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True)
    ordernumber = Column(Integer, ForeignKey("order_numbers.id"))

class OrderNumber(Base):
    __tablename__ = "order_numbers"
    id = Column(Integer, primary_key=True)
    number = Column(String, unique=True)
    creation_date = Column(DateTime, default=func.now())

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()