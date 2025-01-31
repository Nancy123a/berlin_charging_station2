from sqlalchemy import Column, Integer, String, DateTime, Enum, func, ForeignKey
from database.database import Base
from sqlalchemy.orm import relationship

# Define the Report table
class Report(Base):
    __tablename__ = 'report'  # Table name

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(Enum('pending', 'managed', 'resolved'), nullable=False, default='pending')
    description = Column(String, nullable=False)
    severity = Column(Enum('low', 'medium', 'high'), nullable=False, default='low')
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    station_id = Column(Integer, ForeignKey('chargingstation.station_id'))
    user_id = Column(Integer, ForeignKey('user.user_id'))
    admin_id = Column(Integer, ForeignKey('admin.sys_admin_id'))
    csoperator_id = Column(Integer, ForeignKey('csoperators.cs_operator_id'))
    
    user = relationship("User", back_populates="reports")
    admin = relationship("Admin", back_populates="reports")
    csoperator = relationship("CSOperator", back_populates="reports")
    chargingstation = relationship("ChargingStation", back_populates="reports")
    
    