from src.search_context.domain.entities.chargingstation import ChargingStation
from datetime import datetime

class StationUpdateEvent:
    def __init__(self, station_id: int, cs_status: str, success: bool = True):
        self.station_id = station_id
        self.cs_status = cs_status
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<StationUpdateEvent(station_id={self.station_id}, cs_status={self.cs_status}, success={self.success})>"

    def as_dict(self):
        return {
            "station_id": self.station_id,
            "cs_status": self.cs_status,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
