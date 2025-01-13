# src/charging/domain/entities/charging_station.py
from dataclasses import dataclass

@dataclass
class Users:
    user_id: str
    username: str
    password: str
