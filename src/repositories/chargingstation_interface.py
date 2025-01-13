import sys
import os

domain_directory = os.path.abspath(os.path.join(os.getcwd(), '..', 'domain'))

# Add both directories to sys.path
sys.path.append(domain_directory) 

from abc import ABC, abstractmethod
from typing import List
from src.domain.value_objects.post_code import PostalCode
from src.domain.aggregates.charging_station import ChargingStation

class IChargingStationRepository(ABC):
    @abstractmethod
    def find_by_postal_code(self, postal_code: PostalCode) -> List[ChargingStation]:
        """Retrieve all charging stations for a given postal code."""
        pass
    @abstractmethod
    def is_table_empty(self) -> bool:
        """Check if table has data"""
        pass