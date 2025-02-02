from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from src.search_context.domain.entities.chargingstation import ChargingStation
from src.search_context.domain.aggregates.chargingstation_aggregate import ChargingStationAggregate  
from database.database import SessionLocal  # Ensure SessionLocal is imported

class ChargingStationRepository:
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()

    def find_by_postal_code(self, postal_code: str) -> List[ChargingStationAggregate]:
        query = text("""
            SELECT * FROM chargingstation 
            WHERE postal_code = :postal_code AND federal_state = 'Berlin' AND cs_status = 'available'
        """)
        rows = self.session.execute(query, {"postal_code": postal_code}).mappings().all()

        return [ChargingStationAggregate(ChargingStation(**row)) for row in rows]


    def is_table_empty(self) -> bool:
        """Check if the charging station table is empty."""
        query = text("SELECT * FROM chargingstation LIMIT 1")
        result = self.session.execute(query).fetchone()
        return result is None
    
    def update_charging_station(self, id: int, status: str) -> bool:
        """Update a charging station in the database."""
        query = text("UPDATE chargingstation SET cs_status = :status WHERE station_id = :id")
        self.session.execute(query, {"id": id, "status": status})
        self.session.commit()
        return True
