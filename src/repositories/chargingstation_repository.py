import sys
import os

# Get the absolute paths to f1 and f2 directories
domain_directory = os.path.abspath(os.path.join(os.getcwd(), '..', '..', 'domain'))
repository_directory = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))

# Add both directories to sys.path
sys.path.append(domain_directory)  
sys.path.append(repository_directory) 

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from src.domain.value_objects.post_code import PostalCode  # Correct relative import
from src.domain.aggregates.charging_station import ChargingStation
from .chargingstation_interface import IChargingStationRepository

class ChargingStationRepository(IChargingStationRepository):
    def __init__(self, session: Session):
        """Initialize the repository with a SQLAlchemy session."""
        self.session = session

    def find_by_postal_code(self, postal_code: PostalCode) -> List[ChargingStation]:
        
        query = text(f"""SELECT * FROM chargingstation WHERE postal_code = :postal_code AND federal_state = 'Berlin'""")

        result = self.session.execute(query,{"postal_code": postal_code.value})

        return result.fetchall()

    def is_table_empty(self) -> bool:
        query = text("SELECT * FROM chargingstation")
        result = self.session.execute(query).fetchone()
        return result is None