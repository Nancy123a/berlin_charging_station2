# src/charging/domain/entities/charging_station.py
from dataclasses import dataclass

@dataclass
class ChargingStation:
    station_id: str
    postal_code: str
    latitude: str
    longitude: str
    location:str
    street: str
    district: str
    federal_state: str
    operator: str
    power_charging_dev: int
    type_charging_device: str
    commission_date: str
    cs_status:str
