from sqlalchemy import Column, Integer, String
from database.database import Base  # Ensure Base is imported
from sqlalchemy.orm import relationship

class Admin(Base):
    __tablename__ = 'admin'  # Table name

    sys_admin_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    number_reports_assigned = Column(Integer, nullable=False)
    
    reports = relationship("Report", back_populates="admin")