import pytest
import sys
from pathlib import Path
import os

project_root = Path(os.getcwd()).resolve().parent  # Adjust .parent if needed
sys.path.append(str(project_root))
from src.domain.aggregates.charging_station import ChargingStation

# Helper function for creating valid objects
def create_valid_station():
    return ChargingStation(
        station_id="CS123",
        postal_code="12345",
        latitude="52.5200",
        longitude="13.4050",
        location="Berlin",
        street="Main Street 123",
        district="Mitte",
        federal_state="Berlin",
        operator="GreenCharge",
        power_charging_dev=150,
        type_charging_device="Type 2",
        commission_date="11.10.2020",
        cs_status="Active"
    )

# Happy Path Tests
def test_valid_charging_station_creation():
    station = create_valid_station()
    assert station.station_id == "CS123"
    assert station.postal_code == "12345"
    assert station.latitude == "52.5200"
    assert station.longitude == "13.4050"
    assert station.location == "Berlin"
    assert station.power_charging_dev == 150
    assert station.type_charging_device == "Type 2"
    assert station.cs_status == "Active"

# Edge Case Tests
def test_min_max_power_charging_dev():
    station_min = ChargingStation(
        station_id="CS124",
        postal_code="54321",
        latitude="48.8566",
        longitude="2.3522",
        location="Paris",
        street="Some Street",
        district="Central",
        federal_state="Ile-de-France",
        operator="ChargeIt",
        power_charging_dev=1,
        type_charging_device="Type 1",
        commission_date="11.10.2020",
        cs_status="Inactive"
    )
    assert station_min.power_charging_dev == 1

    station_max = create_valid_station()
    station_max.power_charging_dev = 1200
    assert station_max.power_charging_dev == 1200

# Error Scenario Tests
def test_invalid_station_id():
    with pytest.raises(ValueError, match="Station ID must be a non-empty string."):
        ChargingStation(
            station_id="",
            postal_code="12345",
            latitude="52.5200",
            longitude="13.4050",
            location="Berlin",
            street="Main Street 123",
            district="Mitte",
            federal_state="Berlin",
            operator="GreenCharge",
            power_charging_dev=150,
            type_charging_device="Type 2",
            commission_date="211.10.2020",
            cs_status="Active"
        )

def test_invalid_power_charging_dev():
    with pytest.raises(ValueError, match="Power must be a positive integer."):
        ChargingStation(
            station_id="CS125",
            postal_code="12345",
            latitude="52.5200",
            longitude="13.4050",
            location="Berlin",
            street="Main Street 123",
            district="Mitte",
            federal_state="Berlin",
            operator="GreenCharge",
            power_charging_dev=0,
            type_charging_device="Type 2",
            commission_date="11.10.2020",
            cs_status="Active"
        )

    with pytest.raises(ValueError, match="Power must be a positive integer."):
        ChargingStation(
            station_id="CS126",
            postal_code="12345",
            latitude="52.5200",
            longitude="13.4050",
            location="Berlin",
            street="Main Street 123",
            district="Mitte",
            federal_state="Berlin",
            operator="GreenCharge",
            power_charging_dev=-100,
            type_charging_device="Type 2",
            commission_date="11.10.2020",
            cs_status="Active"
        )

def test_edge_case_power_charging_device():
    """Test edge cases for power_charging_dev (minimum and maximum)."""
    station_low = ChargingStation(
        station_id="CS67890",
        postal_code="10115",
        latitude="52.5300",
        longitude="13.4050",
        location="Berlin Center",
        street="Alexanderplatz 1",
        district="Mitte",
        federal_state="Berlin",
        operator="ChargePoint",
        power_charging_dev=1,
        type_charging_device="Slow Charger",
        commission_date="11.10.2020",
        cs_status="Active"
    )
    station_high = ChargingStation(
        station_id="CS99999",
        postal_code="10115",
        latitude="52.5300",
        longitude="13.4050",
        location="Berlin Center",
        street="Alexanderplatz 1",
        district="Mitte",
        federal_state="Berlin",
        operator="ChargePoint",
        power_charging_dev=1200,
        type_charging_device="Ultra-Fast Charger",
        commission_date="11.10.2020",
        cs_status="Active"
    )
    assert station_low.power_charging_dev == 1
    assert station_high.power_charging_dev == 1200


def test_invalid_status():
    with pytest.raises(ValueError, match="Invalid status. Must be 'Active', 'Out Of Service', or 'Under Maintenance'."):
        ChargingStation(
            station_id="CS127",
            postal_code="12345",
            latitude="52.5200",
            longitude="13.4050",
            location="Berlin",
            street="Main Street 123",
            district="Mitte",
            federal_state="Berlin",
            operator="GreenCharge",
            power_charging_dev=150,
            type_charging_device="Type 2",
            commission_date="11.10.2020",
            cs_status="Unknown Status"
        )

def test_empty_fields():
    """Test that required fields cannot be empty."""
    with pytest.raises(ValueError):
        ChargingStation(
            station_id="",
            postal_code="",
            latitude="",
            longitude="",
            location="",
            street="",
            district="",
            federal_state="",
            operator="",
            power_charging_dev=120,
            type_charging_device="Fast Charger",
            commission_date="",
            cs_status="Active"
        )

def test_commission_date_format():
    """Test valid and invalid formats for commission_date."""
    valid_station = ChargingStation(
        station_id="CS00001",
        postal_code="10115",
        latitude="52.5300",
        longitude="13.4050",
        location="Berlin Center",
        street="Alexanderplatz 1",
        district="Mitte",
        federal_state="Berlin",
        operator="ChargePoint",
        power_charging_dev=120,
        type_charging_device="Fast Charger",
        commission_date="11.10.2020",
        cs_status="Active"
    )
    assert valid_station.commission_date == "11.10.2020"

    with pytest.raises(ValueError):
        ChargingStation(
            station_id="CS00002",
            postal_code="10115",
            latitude="52.5300",
            longitude="13.4050",
            location="Berlin Center",
            street="Alexanderplatz 1",
            district="Mitte",
            federal_state="Berlin",
            operator="ChargePoint",
            power_charging_dev=120,
            type_charging_device="Fast Charger",
            commission_date="2020-11-10",  # Invalid format
            cs_status="Active"
        )
        

# Domain Rule Tests
def test_domain_rule_valid_status():
    station_active = create_valid_station()
    assert station_active.cs_status == "Active"

    station_inactive = create_valid_station()
    station_inactive.cs_status = "Out Of Service"
    assert station_inactive.cs_status == "Out Of Service"

    station_maintenance = create_valid_station()
    station_maintenance.cs_status = "Under Maintenance"
    assert station_maintenance.cs_status == "Under Maintenance"
