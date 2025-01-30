from src.search_context.domain.entities.chargingstation import ChargingStation

class StationNotFoundEvent:
    def __init__(self, charging_station: ChargingStation, success: bool = True):
        self.station_id = charging_station.station_id
        self.postal_code = charging_station.postal_code
        self.latitude = charging_station.latitude
        self.longitude = charging_station.longitude
        self.location = charging_station.location
        self.street = charging_station.street
        self.district = charging_station.district
        self.federal_state = charging_station.federal_state
        self.operator = charging_station.operator
        self.power_charging_dev = charging_station.power_charging_dev
        self.commission_date = charging_station.commission_date
        self.type_charging_device = charging_station.type_charging_device
        self.cs_status = charging_station.cs_status
        self.success = success
        self.timestamp = datetime.utcnow()

    def __repr__(self):
        return f"<StationNotFoundEvent(station_id={self.station_id}, postal_code={self.postal_code}, location={self.location}, success={self.success})>"

    def as_dict(self):
        return {
            "station_id": self.station_id,
            "postal_code": self.postal_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location": self.location,
            "street": self.street,
            "district": self.district,
            "federal_state": self.federal_state,
            "operator": self.operator,
            "power_charging_dev": self.power_charging_dev,
            "commission_date": self.commission_date.isoformat() if self.commission_date else None,
            "type_charging_device": self.type_charging_device,
            "cs_status": self.cs_status,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
