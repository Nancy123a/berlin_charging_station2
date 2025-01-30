from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from src.search_context.domain.entities.chargingstation import ChargingStation
from src.search_context.domain.aggregates.chargingstation_aggregate import ChargingStationAggregate  
from database.database import SessionLocal  # Ensure SessionLocal is imported

class ChargingStationRepository:
    def __init__(self, session: Session = None):
        """Initialize the repository with a SQLAlchemy session."""
        self.session = session or SessionLocal()

    def find_by_postal_code(self, postal_code: str) -> List[ChargingStationAggregate]:
        """Find charging stations by postal code and return ChargingStationAggregate objects."""
        
        query = text("""
            SELECT * FROM chargingstation 
            WHERE postal_code = :postal_code AND federal_state = 'Berlin'
        """)

    
        result = self.session.execute(query, {"postal_code": postal_code}).mappings()
        rows = result.all()  # Fetch all results

        charging_stations = []
        for row in rows:
            charging_station = ChargingStation(
                station_id=row["station_id"],
                postal_code=row["postal_code"],
                latitude=row["latitude"],
                longitude=row["longitude"],
                location=row["location"],
                street=row["street"],
                district=row["district"],
                federal_state=row["federal_state"],
                operator=row["operator"],
                power_charging_dev=row["power_charging_dev"],
                commission_date=row["commission_date"],
                type_charging_device=row["type_charging_device"],
                cs_status=row["cs_status"]
            )
            aggregate = ChargingStationAggregate(charging_station)
            charging_stations.append(aggregate)
        
        return charging_stations

    def is_table_empty(self) -> bool:
        """Check if the charging station table is empty."""
        query = text("SELECT * FROM chargingstation LIMIT 1")
        result = self.session.execute(query).fetchone()
        return result is None
