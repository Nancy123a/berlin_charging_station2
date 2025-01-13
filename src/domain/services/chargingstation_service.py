from typing import List
from src.domain.value_objects.post_code import PostalCode
from src.repositories.chargingstation_repository import ChargingStationRepository
from src.domain.aggregates.charging_station import ChargingStation

class ChargingStationService:
    def __init__(self, repository: ChargingStationRepository):
        self.repository = repository

    def find_stations_by_postal_code(self, postal_code: PostalCode) -> List[ChargingStation]:
        """Find charging stations by postal code."""
        return self.repository.find_by_postal_code(postal_code)
    def is_table_empty(self) -> bool:
        return self.repository.is_table_empty()