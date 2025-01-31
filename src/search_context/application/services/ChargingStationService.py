from src.search_context.domain.entities.chargingstation import ChargingStation
from src.search_context.domain.aggregates.chargingstation_aggregate import ChargingStationAggregate
from src.search_context.infrastructure.repositories.ChargingStationRepository import ChargingStationRepository
from src.search_context.domain.events.StationNotFoundEvent import StationNotFoundEvent
from src.search_context.domain.value_objects.postal_code import PostalCode
from typing import List, Union

class ChargingStationService:
    def __init__(self, station_repository: ChargingStationRepository):
        """Initialize with the repository."""
        self.chargingstation_repository = station_repository

    def verify_postal_code(self,postcode:str):
        return PostalCode(postcode)

    def find_stations_by_postal_code(self, postal_code: str) -> Union[List[ChargingStationAggregate], StationNotFoundEvent]:
        """Retrieve a list of ChargingStation aggregates by postal code."""
        
        # Retrieve charging stations from the repository
        charging_stations = self.chargingstation_repository.find_by_postal_code(postal_code)
        
        if not charging_stations:
            # If no stations are found, return a StationNotFoundEvent
            event = StationNotFoundEvent(
                ChargingStation(
                    station_id=None, 
                    postal_code=postal_code, 
                    latitude=None, 
                    longitude=None,
                    location=None, 
                    street=None, 
                    district=None, 
                    federal_state=None, 
                    operator=None, 
                    power_charging_dev=None, 
                    commission_date=None, 
                    type_charging_device=None, 
                    cs_status=None
                )
            )
            return event

        # Return the found ChargingStation aggregates
        return charging_stations

    def is_table_empty(self) -> bool:
        return self.chargingstation_repository.is_table_empty()