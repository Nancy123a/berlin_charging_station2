# src/charging/domain/entities/charging_station.py
from dataclasses import dataclass

@dataclass
class Csoperator:
    cs_operator_id: str
    username: str
    password: str
    number_reports_assigned:int