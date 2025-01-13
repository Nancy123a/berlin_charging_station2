from sqlalchemy import Column, Integer, String, Float
from src.sqldatabase.database import engine,SessionLocal,Base

# Define the User table
class User(Base):
    __tablename__ = 'users'  # Table name

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


