from datetime import datetime
from src.search_context.domain.entities.chargingstation import ChargingStation
from src.search_context.domain.events.StationFoundEvent import StationFoundEvent

class ChargingStationAggregate:
    def __init__(self, charging_station: ChargingStation):
        self.charging_station = charging_station
        self.events = []

    def change_station_status(self, new_status: str):
        """Change the status of the charging station (e.g., Available, In Use, Out of Service)."""
        if self.charging_station.cs_status == new_status:
            raise ValueError("The station is already in this status.")  # Ensure we don't make redundant changes
        self.charging_station.cs_status = new_status
        self._record_event()

    def commission_station(self, commission_date: datetime):
        """Set the commission date and mark the station as operational."""
        if self.charging_station.commission_date is not None:
            raise ValueError("This station has already been commissioned.")
        self.charging_station.commission_date = commission_date
        self.charging_station.cs_status = "Available"  # Mark as available after commissioning
        self._record_event()

    def _record_event(self):
        """Record an event when a state change occurs."""
        event = StationFoundEvent(self.charging_station)
        self.events.append(event)

    def get_uncommitted_events(self):
        """Return all the events that have not been committed yet."""
        return self.events

    def clear_events(self):
        """Clear the list of events after they have been committed."""
        self.events = []

    def apply(self, event):
        """Apply an event to the aggregate (can be used to replay events)."""
        if isinstance(event, StationFoundEvent):
            self.charging_station = ChargingStation(
                station_id=event.station_id,
                postal_code=event.postal_code,
                latitude=event.latitude,
                longitude=event.longitude,
                location=event.location,
                street=event.street,
                district=event.district,
                federal_state=event.federal_state,
                operator=event.operator,
                power_charging_dev=event.power_charging_dev,
                commission_date=event.commission_date,
                type_charging_device=event.type_charging_device,
                cs_status=event.cs_status
            )

    def __repr__(self):
        return f"<ChargingStationAggregate(station_id={self.charging_station.station_id}, status={self.charging_station.cs_status})>"

