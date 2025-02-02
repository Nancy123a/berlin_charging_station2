from src.search_context.domain.entities.chargingstation import ChargingStation
from src.search_context.domain.aggregates.chargingstation_aggregate import ChargingStationAggregate
from src.search_context.infrastructure.repositories.ChargingStationRepository import ChargingStationRepository
from src.search_context.domain.events.StationNotFoundEvent import StationNotFoundEvent
from src.search_context.domain.events.PostalCodeNotFoundEvent import PostalCodeNotFoundEvent
from src.search_context.domain.events.PostalCodeFoundEvent import PostalCodeFoundEvent
from src.search_context.domain.events.StationFoundEvent import StationFoundEvent
from src.search_context.domain.value_objects.postal_code import PostalCode
from typing import List, Union
from src.search_context.domain.events.StationUpdateEvent import StationUpdateEvent

class ChargingStationService:
    def __init__(self, station_repository: ChargingStationRepository):
        self.station_repository = station_repository

    def verify_postal_code(self, postcode: str):
        try:
            return PostalCodeFoundEvent(PostalCode(postcode))
        except ValueError as e:
            return PostalCodeNotFoundEvent(PostalCode(postcode), str(e))

    def find_stations_by_postal_code(self, postal_code: str):
        stations = self.station_repository.find_by_postal_code(postal_code)
        return StationFoundEvent(stations) if stations else StationNotFoundEvent(ChargingStation(postal_code=postal_code))


    def is_table_empty(self) -> bool:
        return self.station_repository.is_table_empty()
    
    def update_charging_station(self, id: int, status: str) -> StationUpdateEvent:
        success = self.station_repository.update_charging_station(id, status)
        return StationUpdateEvent(id, status, success)