from sqlalchemy import Column, Integer, String, DateTime, Enum, func, ForeignKey, Boolean
from database.database import Base
from sqlalchemy.orm import relationship

# Define the Notification table
class Notification(Base):
    __tablename__ = 'notification'  # Table name

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    user_id = Column(Integer, ForeignKey('user.user_id'))
    user = relationship("User", back_populates="notifications")
    