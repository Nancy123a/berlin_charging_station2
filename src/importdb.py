import pandas as pd
import os
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.sqldatabase.database import SessionLocal, engine, Base
from src.sqldatabase.hub.users import User
from src.sqldatabase.hub.chargingstation import ChargingStation
import uuid
import re

def import_charging_stations_from_csv(df):
    # Load CSV file
    print('I HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')

    # Ensure the column names match the database schema
    column_mapping = {
        "Postleitzahl": "postal_code",
        "Breitengrad": "latitude",
        "Längengrad": "longitude",
        "Ort": "location",
        "Straße": "street",
        "Kreis/kreisfreie Stadt": "district",
        "Bundesland": "federal_state",
        "Betreiber": "operator",
        "Nennleistung Ladeeinrichtung [kW]": "power_charging_dev",
        "Art der Ladeeinrichung": "type_charging_device",
        "Inbetriebnahmedatum": "commission_date"
    }

    # Rename columns according to the mapping
    df = df.rename(columns=column_mapping)

    # Initialize the database session
    session = SessionLocal()

    # Insert data into the database
    for _, row in df.iterrows():
        # Generate a unique station_id if it's not in the CSV
        station_id = str(uuid.uuid4())

            
        # Create the charging station object with the generated station_id
        charging_station = ChargingStation(
            station_id=station_id,
            postal_code=str(row["postal_code"]).split('.')[0],
            latitude=row["latitude"],
            longitude=row["longitude"],
            street=row["street"],
            district=row["district"],
            location=row["location"],
            federal_state=row["federal_state"],
            operator=row["operator"],
            power_charging_dev=row["power_charging_dev"],
            type_charging_device=row["type_charging_device"],
            commission_date=row["commission_date"],
            cs_status="Available"  # Default status
        )

        # Add and commit the data
        session.add(charging_station)

    session.commit()
    session.close()
    print("Data successfully imported! HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")

if __name__ == "__main__":
    import_charging_stations_from_csv("../datasets/Ladesaeulenregister.csv")



