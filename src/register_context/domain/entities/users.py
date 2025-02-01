from sqlalchemy import Column, Integer, String, Float
from database.database import engine,SessionLocal,Base
from sqlalchemy.orm import relationship

# Define the User table
class User(Base):
    __tablename__ = 'user'  # Table name

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    
    reports = relationship("Report", back_populates="user")
    notifications = relationship("Notification", back_populates="user")