import pandas as pd
import uuid
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from database.database import SessionLocal
from src.search_context.domain.entities.chargingstation import ChargingStation

def convert_to_date(date_str):
    """Converts a date string to a datetime.date object."""
    if pd.isna(date_str) or date_str is None:
        return None  # Handle missing dates
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").date()  # Ensure correct format
    except ValueError:
        return None  # Handle incorrect format

def clean_number(value):
    """Converts a number string with commas to a float."""
    if pd.isna(value) or value is None:
        return None
    return float(str(value).replace(",", "."))  # Convert '52,510055' → '52.510055'

def import_charging_stations_from_csv(df):
    print("====> Importing Charging Stations Data")

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

    df = df.rename(columns=column_mapping)

    # Convert data types to match SQLite schema
    df["commission_date"] = df["commission_date"].apply(convert_to_date)
    df["latitude"] = df["latitude"].apply(clean_number)  # Convert to float
    df["longitude"] = df["longitude"].apply(clean_number)  # Convert to float
    df["power_charging_dev"] = df["power_charging_dev"].apply(clean_number)  # Convert to float

    # Initialize database session
    session = SessionLocal()
    charging_stations = []

    for _, row in df.iterrows():
        station_id = uuid.uuid4().int % (2**63) # Generate unique ID
        
        charging_station = ChargingStation(
            station_id=station_id,
            postal_code=str(row["postal_code"]).split('.')[0] if pd.notna(row["postal_code"]) else None,
            latitude=row["latitude"],
            longitude=row["longitude"],
            street=row["street"],
            district=row["district"],
            location=row["location"],
            federal_state=row["federal_state"],
            operator=row["operator"],
            power_charging_dev=row["power_charging_dev"],  # ✅ Converted to float
            type_charging_device=row["type_charging_device"],
            commission_date=row["commission_date"],  # ✅ Converted to date
            cs_status="available"
        )
        charging_stations.append(charging_station)

    session.bulk_save_objects(charging_stations)
    session.commit()
    session.close()
    
    print("✅ Data successfully imported!")

if __name__ == "__main__":
    df = pd.read_csv("../datasets/Ladesaeulenregister.csv")  # Load CSV
    import_charging_stations_from_csv(df)
