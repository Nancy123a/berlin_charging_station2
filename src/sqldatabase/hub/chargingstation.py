from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from src.sqldatabase.database import engine, Base  # Adjust import path as needed


class ChargingStation(Base):
    __tablename__ = "chargingstation"

    station_id = Column(String, primary_key=True, index=True)
    postal_code = Column(String, index=True)
    latitude = Column(String)
    longitude = Column(String)
    location=Column(String)
    street = Column(String)
    district = Column(String)
    federal_state = Column(String)
    operator = Column(String)
    power_charging_dev = Column(Integer)
    commission_date = Column(String)
    type_charging_device=Column(String)
    cs_status=Column(String)
