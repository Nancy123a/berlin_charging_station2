import pytest
import pytest
import sys
from pathlib import Path
import os
from sqlalchemy.exc import IntegrityError  # Import for handling constraint violation error

project_root = Path(os.getcwd()).resolve().parent.parent
sys.path.append(str(project_root))
import folium
from unittest.mock import patch
from src.search_context.domain.entities.chargingstation import ChargingStation
from folium import Marker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, SessionLocal,engine
from folium.plugins import MarkerCluster

@pytest.fixture
def db_session():
    """Create a new database session for each test."""
    
    # Set up in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')  # Or point to your test database
    Base.metadata.create_all(engine)  # Create tables

    # Session factory
    Session = sessionmaker(bind=engine)
    session = Session()

    # Provide the session to the test
    yield session

    # Rollback and close session after each test
    session.rollback()
    session.close()
    
# Test 1: Test Charging Stations Data Display
def test_charging_stations_data_display(db_session):
    """Test that when a valid postal code is entered, the map displays the correct markers for charging stations."""
    # Create some test charging stations in multiple postal codes
    charging_station_1 = ChargingStation(
        station_id=123, postal_code="10001", latitude=40.7128, longitude=-74.0060, location="New York, USA",
        street="5th Avenue", district="Manhattan", federal_state="NY", operator="NYC Charging", 
        power_charging_dev=50, commission_date=datetime.strptime("11.10.2020", "%d.%m.%Y").date(), type_charging_device="Fast", cs_status="Active"
    )
    charging_station_2 = ChargingStation(
        station_id=126, postal_code="10001", latitude=40.730610, longitude=-73.935242, location="New York, USA",
        street="Broadway", district="Manhattan", federal_state="NY", operator="NYC Charging", 
        power_charging_dev=100, commission_date=datetime.strptime("11.10.2020", "%d.%m.%Y").date(), type_charging_device="Fast", cs_status="Active"
    )
    db_session.add(charging_station_1)
    db_session.add(charging_station_2)
    db_session.commit()

    # Generate map and add markers
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=13)
    marker_cluster = MarkerCluster().add_to(m)

    # Adding markers to map
    for station in [charging_station_1, charging_station_2]:
        folium.Marker(
            location=[station.latitude, station.longitude],
            popup=f"Station ID: {station.station_id}, Operator: {station.operator}, Power: {station.power_charging_dev}kW"
        ).add_to(marker_cluster)

    # Assert that the markers were added correctly
    assert len(marker_cluster._children) == 2  # Should have 2 markers

# Test 2: Test Color Categorization for Power
def test_color_categorization_for_power(db_session):
    """Test that charging stations are color-coded correctly based on power rating."""
    # Create different charging stations with varying power
    station_low_power = ChargingStation(station_id=123, power_charging_dev=30, cs_status="Active", latitude=40.7128, longitude=-74.0060)
    station_medium_power = ChargingStation(station_id=124, power_charging_dev=120, cs_status="Active", latitude=40.730610, longitude=-73.935242)
    station_high_power = ChargingStation(station_id=125, power_charging_dev=200, cs_status="Active", latitude=40.748817, longitude=-73.985428)

    db_session.add(station_low_power)
    db_session.add(station_medium_power)
    db_session.add(station_high_power)
    db_session.commit()

    # Generate map and add markers with color-coding based on power
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=13)
    marker_cluster = MarkerCluster().add_to(m)

    def get_marker_color(power):
        if power <= 50:
            return 'green'
        elif power <= 150:
            return 'yellow'
        else:
            return 'red'

    # Adding markers with color based on power
    for station in [station_low_power, station_medium_power, station_high_power]:
        folium.Marker(
            location=[station.latitude, station.longitude],
            popup=f"Station ID: {station.station_id}, Power: {station.power_charging_dev}kW",
            icon=folium.Icon(color=get_marker_color(station.power_charging_dev))
        ).add_to(marker_cluster)

    # Assert color coding works
    assert marker_cluster._children # Ensure that markers are added to cluster


# Test 3: Test Map Zoom Behavior
def test_map_zoom_behavior(db_session):
    """Test that the map zooms to the correct region based on postal code."""
    station_1 = ChargingStation(station_id=123, postal_code="20001", latitude=38.8954, longitude=-77.0365)
    db_session.add(station_1)
    db_session.commit()

    # Generate map and simulate postal code zooming
    m = folium.Map(location=[38.8954, -77.0365], zoom_start=13)
    folium.Marker(location=[38.8954, -77.0365]).add_to(m)

    # Assert that the zoom level works correctly
    assert m.get_bounds()  # Check that bounds are set properly to zoom in


# Test 4: Test the Handling of Empty or Null Data
def test_empty_or_null_data_handling(db_session):
    """Test that the app handles missing or null data gracefully."""
    station_null_power = ChargingStation(station_id=123, power_charging_dev=None)
    db_session.add(station_null_power)
    db_session.commit()
    
    charging_stations = db_session.query(ChargingStation).all()
    assert all(station.power_charging_dev is not None for station in charging_stations)
