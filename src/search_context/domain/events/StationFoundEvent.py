from typing import List
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.search_context.domain.aggregates.chargingstation_aggregate import ChargingStationAggregate

class StationFoundEvent:
    def __init__(self, stations: List["ChargingStationAggregate"], success: bool = True):
        self.stations = stations
        self.timestamp = datetime.utcnow()
        self.success = success  

    def __repr__(self):
        return f"<StationFoundEvent(stations={len(self.stations)}, success={self.success})>"

    def as_dict(self):
        return {
            "stations": [station.as_dict() for station in self.stations],  
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
