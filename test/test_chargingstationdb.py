import pytest
import sys
from pathlib import Path
import os
from sqlalchemy.exc import IntegrityError  # For handling constraint violation error

project_root = Path(os.getcwd()).resolve().parent  # Adjust .parent if needed
sys.path.append(str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.sqldatabase.database import Base, SessionLocal
from src.sqldatabase.hub.chargingstation import ChargingStation  

# Helper functions to interact with the database
def create_charging_station_in_db(db_session, charging_station):
    """Create a new ChargingStation in the database."""
    db_station = ChargingStation(
        station_id=charging_station.station_id,
        postal_code=charging_station.postal_code,
        latitude=charging_station.latitude,
        longitude=charging_station.longitude,
        location=charging_station.location,
        street=charging_station.street,
        district=charging_station.district,
        federal_state=charging_station.federal_state,
        operator=charging_station.operator,
        power_charging_dev=charging_station.power_charging_dev,
        commission_date=charging_station.commission_date,
        type_charging_device=charging_station.type_charging_device,
        cs_status=charging_station.cs_status
    )
    db_session.add(db_station)
    db_session.commit()
    db_session.refresh(db_station)
    return db_station

def get_charging_station_by_station_id(db_session, station_id: str):
    """Fetch a ChargingStation from the database by station_id."""
    return db_session.query(ChargingStation).filter(ChargingStation.station_id == station_id).first()

def get_charging_station_by_postal_code(db_session, postal_code: str):
    """Fetch a ChargingStation from the database by postal_code."""
    return db_session.query(ChargingStation).filter(ChargingStation.postal_code == postal_code).first()

@pytest.fixture(scope="module")
def db_session():
    # Set up in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)  # Create all tables

    session = SessionLocal(bind=engine)  # Create session for testing
    yield session
    session.rollback()  # Rollback any changes after test
    session.close()
    Base.metadata.drop_all(bind=engine)  # Clean up after test

def test_create_charging_station(db_session):
    """Test creating a ChargingStation in the database."""
    new_station = ChargingStation(
        station_id="CS001", postal_code="12345", latitude="52.5200", longitude="13.4050",
        location="Berlin, Germany", street="Unter den Linden", district="Mitte", federal_state="Berlin",
        operator="Berlin Charging", power_charging_dev=5, commission_date="11.10.2020",
        type_charging_device="Fast", cs_status="Active"
    )
    created_station = create_charging_station_in_db(db_session, new_station)
    
    assert created_station.station_id == "CS001"
    assert created_station.postal_code == "12345"
    assert created_station.latitude == "52.5200"
    assert created_station.longitude == "13.4050"
    assert created_station.location == "Berlin, Germany"
    assert created_station.street == "Unter den Linden"
    assert created_station.district == "Mitte"
    assert created_station.federal_state == "Berlin"
    assert created_station.operator == "Berlin Charging"
    assert created_station.power_charging_dev == 5
    assert created_station.commission_date == "11.10.2020"
    assert created_station.type_charging_device == "Fast"
    assert created_station.cs_status == "Active"

def test_get_charging_station_by_station_id(db_session):
    """Test fetching a ChargingStation from the database by station_id."""
    new_station = ChargingStation(
        station_id="CS002", postal_code="67890", latitude="48.8566", longitude="2.3522",
        location="Paris, France", street="Champs-Élysées", district="8th Arrondissement", federal_state="Île-de-France",
        operator="Paris Charging", power_charging_dev=3, commission_date="11.10.2020",
        type_charging_device="SuperFast", cs_status="Inactive"
    )
    created_station = create_charging_station_in_db(db_session, new_station)
    fetched_station = get_charging_station_by_station_id(db_session, created_station.station_id)
    
    assert fetched_station is not None
    assert fetched_station.station_id == "CS002"
    assert fetched_station.postal_code == "67890"
    assert fetched_station.latitude == "48.8566"
    assert fetched_station.longitude == "2.3522"
    assert fetched_station.location == "Paris, France"
    assert fetched_station.street == "Champs-Élysées"
    assert fetched_station.district == "8th Arrondissement"
    assert fetched_station.federal_state == "Île-de-France"
    assert fetched_station.operator == "Paris Charging"
    assert fetched_station.power_charging_dev == 3
    assert fetched_station.commission_date == "11.10.2020"
    assert fetched_station.type_charging_device == "SuperFast"
    assert fetched_station.cs_status == "Inactive"

def test_get_charging_station_by_postal_code(db_session):
    """Test fetching a ChargingStation from the database by postal_code."""
    new_station = ChargingStation(
        station_id="CS003", postal_code="54321", latitude="40.7128", longitude="-74.0060",
        location="New York, USA", street="Wall Street", district="Manhattan", federal_state="New York",
        operator="NYC Charging", power_charging_dev=7, commission_date="11.10.2020",
        type_charging_device="UltraFast", cs_status="Active"
    )
    created_station = create_charging_station_in_db(db_session, new_station)
    
    # Fetch by postal_code
    fetched_station = get_charging_station_by_postal_code(db_session, created_station.postal_code)
    
    assert fetched_station is not None
    assert fetched_station.station_id == "CS003"
    assert fetched_station.postal_code == "54321"
    assert fetched_station.latitude == "40.7128"
    assert fetched_station.longitude == "-74.0060"
    assert fetched_station.location == "New York, USA"
    assert fetched_station.street == "Wall Street"
    assert fetched_station.district == "Manhattan"
    assert fetched_station.federal_state == "New York"
    assert fetched_station.operator == "NYC Charging"
    assert fetched_station.power_charging_dev == 7
    assert fetched_station.commission_date == "11.10.2020"
    assert fetched_station.type_charging_device == "UltraFast"
    assert fetched_station.cs_status == "Active"
    
def test_add_invalid_charging_station(db_session):
    """Test adding an invalid ChargingStation (e.g., missing required fields or invalid data)."""
    
    # Test 1: Missing required field 'station_id' (unique constraint violation)
    with pytest.raises(IntegrityError):
        invalid_station = ChargingStation(
            station_id=None,  # 'None' is invalid for a primary key field
            postal_code="00000", latitude="51.5074", longitude="-0.1278",
            location="London, UK", street="Baker Street", district="Westminster", federal_state="London",
            operator="London Charging", power_charging_dev=4, commission_date="11.10.2020",
            type_charging_device="Fast", cs_status="Active"
        )
        create_charging_station_in_db(db_session, invalid_station)
    
    # Test 2: Duplicate station_id
    with pytest.raises(IntegrityError):
        invalid_station = ChargingStation(
            station_id="CS001", postal_code="99999", latitude="52.2050", longitude="0.1218",
            location="Cambridge, UK", street="King's Parade", district="City Centre", federal_state="Cambridge",
            operator="Cambridge Charging", power_charging_dev=6, commission_date="11.11.2021",
            type_charging_device="SuperFast", cs_status="Active"
        )
        create_charging_station_in_db(db_session, invalid_station)  # Duplicate station_id
    
    # Test 3: Invalid data type for power_charging_dev (should be integer)
    with pytest.raises(DataError):
        invalid_station = ChargingStation(
            station_id="CS004", postal_code="98765", latitude="34.0522", longitude="-118.2437",
            location="Los Angeles, USA", street="Hollywood Blvd", district="Hollywood", federal_state="California",
            operator="LA Charging", power_charging_dev="five", commission_date="11.10.2020",
            type_charging_device="Fast", cs_status="Inactive"
        )
        create_charging_station_in_db(db_session, invalid_station)

def test_get_charging_station_by_postal_code_not_found(db_session):
    """Test fetching a ChargingStation by postal_code when no station exists with the given postal code."""
    
    # Attempt to fetch a charging station with a postal code that doesn't exist
    non_existent_postal_code = "00000"
    fetched_station = get_charging_station_by_postal_code(db_session, non_existent_postal_code)
    
    # Assert that no station is found
    assert fetched_station is None

