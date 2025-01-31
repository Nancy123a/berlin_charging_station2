import pytest
import sys
from pathlib import Path
import os
from datetime import datetime

# Dynamically set the project root to find `src`
project_root = Path(os.getcwd()).resolve().parent.parent    # Adjust based on depth
sys.path.append(str(project_root))

from database.database import Base  # Ensure correct database import
from src.search_context.domain.entities.chargingstation import ChargingStation


# Helper function for creating valid objects
def create_valid_station():
    return ChargingStation(
        station_id=123,  # Ensure this is an integer
        postal_code="12345",
        latitude=52.5200,  # Convert from string to float
        longitude=13.4050,  # Convert from string to float
        location="Berlin",
        street="Main Street 123",
        district="Mitte",
        federal_state="Berlin",
        operator="GreenCharge",
        power_charging_dev=150,
        type_charging_device="Type 2",
        commission_date=datetime.strptime("11.10.2020", "%d.%m.%Y").date(),  # Ensure this is a date object
        cs_status="Active"
    )


# Happy Path Test
def test_valid_charging_station_creation():
    station = create_valid_station()
    assert station.station_id == 123
    assert station.postal_code == "12345"
    assert station.latitude == 52.5200
    assert station.longitude == 13.4050
    assert station.location == "Berlin"
    assert station.power_charging_dev == 150
    assert station.type_charging_device == "Type 2"
    assert station.cs_status == "Active"


# Edge Case Tests
def test_min_max_power_charging_dev():
    station_min = ChargingStation(
        station_id=124,
        postal_code="54321",
        latitude=48.8566,
        longitude=2.3522,
        location="Paris",
        street="Some Street",
        district="Central",
        federal_state="Ile-de-France",
        operator="ChargeIt",
        power_charging_dev=1,
        type_charging_device="Type 1",
        commission_date=datetime.strptime("11.10.2020", "%d.%m.%Y").date(),
        cs_status="Inactive"
    )
    assert station_min.power_charging_dev == 1

    station_max = create_valid_station()
    station_max.power_charging_dev = 1200
    assert station_max.power_charging_dev == 1200


# Error Scenario Tests
def test_invalid_station_id():
    with pytest.raises(ValueError, match="Station ID must be a non-empty integer."):
        ChargingStation(
            station_id=None,  # Invalid
            postal_code="12345",
            latitude=52.5200,
            longitude=13.4050,
            location="Berlin",
            street="Main Street 123",
            district="Mitte",
            federal_state="Berlin",
            operator="GreenCharge",
            power_charging_dev=150,
            type_charging_device="Type 2",
            commission_date=datetime.strptime("11.10.2020", "%d.%m.%Y").date(),
            cs_status="Active"
        )


def test_invalid_power_charging_dev():
    with pytest.raises(ValueError, match="Power must be a positive number."):
        ChargingStation(
            station_id=125,
            postal_code="12345",
            latitude=52.5200,
            longitude=13.4050,
            location="Berlin",
            street="Main Street 123",
            district="Mitte",
            federal_state="Berlin",
            operator="GreenCharge",
            power_charging_dev=0,  # Invalid
            type_charging_device="Type 2",
            commission_date=datetime.strptime("11.10.2020", "%d.%m.%Y").date(),
            cs_status="Active"
        )


def test_invalid_status():
    with pytest.raises(ValueError, match="Invalid status. Must be 'Active', 'Out Of Service', or 'Under Maintenance'."):
        ChargingStation(
            station_id=127,
            postal_code="12345",
            latitude=52.5200,
            longitude=13.4050,
            location="Berlin",
            street="Main Street 123",
            district="Mitte",
            federal_state="Berlin",
            operator="GreenCharge",
            power_charging_dev=150,
            type_charging_device="Type 2",
            commission_date=datetime.strptime("11.10.2020", "%d.%m.%Y").date(),
            cs_status="Unknown Status"  # Invalid
        )


def test_empty_fields():
    """Test that required fields cannot be empty."""
    with pytest.raises(ValueError):
        ChargingStation(
            station_id=None,
            postal_code="",
            latitude=None,
            longitude=None,
            location="",
            street="",
            district="",
            federal_state="",
            operator="",
            power_charging_dev=120,
            type_charging_device="Fast Charger",
            commission_date=None,
            cs_status="Active"
        )


def test_commission_date_format():
    """Test valid and invalid formats for commission_date."""
    valid_station = ChargingStation(
        station_id=1,
        postal_code="10115",
        latitude=52.5300,
        longitude=13.4050,
        location="Berlin Center",
        street="Alexanderplatz 1",
        district="Mitte",
        federal_state="Berlin",
        operator="ChargePoint",
        power_charging_dev=120,
        type_charging_device="Fast Charger",
        commission_date=datetime.strptime("11.10.2020", "%d.%m.%Y").date(),
        cs_status="Active"
    )
    assert valid_station.commission_date == datetime.strptime("11.10.2020", "%d.%m.%Y").date()

    with pytest.raises(ValueError):
        ChargingStation(
            station_id=2,
            postal_code="10115",
            latitude=52.5300,
            longitude=13.4050,
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
