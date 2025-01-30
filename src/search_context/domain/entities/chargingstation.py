from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from database.database import Base  # Adjust import path as needed

class ChargingStation(Base):
    __tablename__ = "chargingstation"

    station_id = Column(Integer, primary_key=True, index=True) 
    postal_code = Column(String, index=True)
    latitude = Column(Float)  
    longitude = Column(Float)  
    location = Column(String)
    street = Column(String)
    district = Column(String)
    federal_state = Column(String)
    operator = Column(String)
    power_charging_dev = Column(Float) 
    commission_date = Column(Date)
    type_charging_device = Column(String)
    cs_status = Column(String)
