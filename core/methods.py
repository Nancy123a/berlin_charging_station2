import pandas                        as pd
import geopandas                     as gpd
import core.HelperTools              as ht

import folium
# from folium.plugins import HeatMap
import streamlit as st
from streamlit_folium import folium_static
from branca.colormap import LinearColormap
from folium.plugins import HeatMap

import sys
from pathlib import Path
import os

project_root = Path(os.getcwd()).resolve().parent  # Adjust .parent if needed
sys.path.append(str(project_root))

from sqlalchemy import create_engine,inspect
from sqlalchemy.orm import sessionmaker
from src.sqldatabase.database import SessionLocal,engine,Base
from src.domain.value_objects.post_code import PostalCode
from src.repositories.chargingstation_repository import ChargingStationRepository
from src.domain.services.chargingstation_service import ChargingStationService
from src.domain.aggregates.charging_station import ChargingStation
from src import importdb as imp
from geopy.exc import GeocoderTimedOut


def sort_by_plz_add_geometry(dfr, dfg, pdict): 
    dframe                  = dfr.copy()
    df_geo                  = dfg.copy()
    
    sorted_df               = dframe\
        .sort_values(by='PLZ')\
        .reset_index(drop=True)\
        .sort_index()
        
    sorted_df2              = sorted_df.merge(df_geo, on=pdict["geocode"], how ='left')
    sorted_df3              = sorted_df2.dropna(subset=['geometry'])
    
    sorted_df3.loc[:, 'geometry'] = gpd.GeoSeries.from_wkt(sorted_df3['geometry'])
    ret                     = gpd.GeoDataFrame(sorted_df3, geometry='geometry')
    
    return ret

# -----------------------------------------------------------------------------
@ht.timer
def preprop_lstat(dfr, dfg, pdict):
    """Preprocessing dataframe from Ladesaeulenregister.csv"""
    dframe                  = dfr.copy()
    df_geo                  = dfg.copy()
    
    dframe2               	= dframe.loc[:,['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]']]
    dframe2.rename(columns  = {"Nennleistung Ladeeinrichtung [kW]":"KW", "Postleitzahl": "PLZ"}, inplace = True)

    # Convert to string
    dframe2['Breitengrad']  = dframe2['Breitengrad'].astype(str)
    dframe2['Längengrad']   = dframe2['Längengrad'].astype(str)

    # Now replace the commas with periods
    dframe2['Breitengrad']  = dframe2['Breitengrad'].str.replace(',', '.')
    dframe2['Längengrad']   = dframe2['Längengrad'].str.replace(',', '.')

    dframe3                 = dframe2[(dframe2["Bundesland"] == 'Berlin') & 
                                            (dframe2["PLZ"] > 10115) &  
                                            (dframe2["PLZ"] < 14200)]
    
    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    
    return ret
    

# -----------------------------------------------------------------------------
@ht.timer
def count_plz_occurrences(df_lstat2):
    """Counts loading stations per PLZ"""
    # Group by PLZ and count occurrences, keeping geometry
    result_df = df_lstat2.groupby('PLZ').agg(
        Number=('PLZ', 'count'),
        geometry=('geometry', 'first')
    ).reset_index()
    
    return result_df
    
@ht.timer
def preprop_resid(dfr, dfg, pdict):
    """Preprocessing dataframe from plz_einwohner.csv"""
    dframe                  = dfr.copy()
    df_geo                  = dfg.copy()    
    
    dframe2               	= dframe.loc[:,['plz', 'einwohner', 'lat', 'lon']]
    dframe2.rename(columns  = {"plz": "PLZ", "einwohner": "Einwohner", "lat": "Breitengrad", "lon": "Längengrad"}, inplace = True)

    # Convert to string
    dframe2['Breitengrad']  = dframe2['Breitengrad'].astype(str)
    dframe2['Längengrad']   = dframe2['Längengrad'].astype(str)

    # Now replace the commas with periods
    dframe2['Breitengrad']  = dframe2['Breitengrad'].str.replace(',', '.')
    dframe2['Längengrad']   = dframe2['Längengrad'].str.replace(',', '.')

    dframe3                 = dframe2[ 
                                            (dframe2["PLZ"] > 10000) &  
                                            (dframe2["PLZ"] < 14200)]
    
    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    
    return ret

def inspect_db(df):
    session=SessionLocal()
    service=ChargingStationService(ChargingStationRepository(session))
    isempty=service.is_table_empty()
    if isempty:
        imp.import_charging_stations_from_csv(df)


def get_power_category_and_color(power):
    power = float(power)  # Ensure power is a float for comparison
    
    if power <= 50:
        return 'Low Power', 'green'  # Low Power
    elif power <= 150:
        return 'Medium Power', 'yellow'  # Medium Power
    elif power <= 500:
        return 'High Power', 'orange'  # High Power
    else:
        return 'Ultra High Power', 'red'  # Ultra High Power

# -----------------------------------------------------------------------------
@ht.timer
def make_streamlit_electric_Charging_resid(df,dfr1, dfr2,role):
    """Makes Streamlit App with Heatmap of Electric Charging Stations and Residents"""
    inspect_db(df)
    
    if role=="user":
        menu = ["Search Station", "Report Malfunction","Notifications"]
    elif role=="admin":
        menu = ["Search Station", "Manage Malfunction Report","Notifications"]
    elif role=="csoperator":
        menu = ["Search Station", "Resolve Malfunction Report"]
        
    choice = st.sidebar.selectbox("Select Option",menu)

    if choice == "Search Station":
        dframe1 = dfr1.copy()
        dframe2 = dfr2.copy()
    
        # Streamlit app
        st.title('Heatmaps: Electric Charging Stations and Residents')
    
        # Search Box
        search_query = st.text_input("Enter Postal Code (PLZ) to Search:", "")
        search_button = st.button("Search")
    
        # Create a radio button for layer selection
        layer_selection = st.radio("Select Layer", ("Residents", "Charging_Stations"))
    
        # Create a Folium map
        m = folium.Map(location=[52.52, 13.40], zoom_start=10)
    
        # Create a new session
        if layer_selection == "Residents":
            
            # Create a color map for Residents
            color_map = LinearColormap(colors=['yellow', 'red'], vmin=dframe2['Einwohner'].min(), vmax=dframe2['Einwohner'].max())
    
            # Add polygons to the map for Residents
            for idx, row in dframe2.iterrows():
                popup = f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}"
                style = lambda x, color=color_map(row['Einwohner']): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                }
                folium.GeoJson(row['geometry'], style_function=style, tooltip=popup).add_to(m)
            
            # Highlight the searched Postal Code if a valid PLZ is found
            if search_button:
                try:
                    session = SessionLocal()
                    postal_code = PostalCode(search_query)  
                    service=ChargingStationService(ChargingStationRepository(session))
                    charging_stations=service.find_stations_by_postal_code(postal_code)
                    latitudes = []
                    longitudes = []
                    if charging_stations:
                        for station in charging_stations:
                            longitude=float(station.longitude.replace(",", "."))
                            latitude=float(station.latitude.replace(",", "."))
                            latitudes.append(latitude)
                            longitudes.append(longitude)
                            # Get color based on the charging station's power
                            power_category, color = get_power_category_and_color(station.power_charging_dev)
                            popup_content = f"""
                            <div style="font-size: 14px;">
                            <h4 style="color: #007bff;">Charging Station Information</h4>
                            <strong>Street:</strong> {station.street}<br>
                            <strong>District:</strong> {station.district}<br>
                            <strong>Location:</strong> {station.location}<br>
                            <strong>Power Charging Device:</strong> {station.power_charging_dev} kW<br>
                            <strong>Charging Device Type:</strong> {station.type_charging_device}<br>
                            <strong>Operator:</strong> {station.operator}<br>
                            <strong>Power Category:</strong> {power_category}<br><br>
                            <p style="color: #888; font-size: 12px;">Click on the marker for more details.</p>
                            </div>
                            """

                            folium.Marker(
                                location=[latitude, longitude],
                                popup=folium.Popup(popup_content, max_width=300),
                                icon=folium.Icon(color=color, icon='cloud')
                            ).add_to(m)

                        min_latitude=min(latitudes)
                        min_longitude=min(longitudes)
                        max_latitude=max(latitudes)
                        max_longitude=max(longitudes)
                        m.fit_bounds([[min_latitude, min_longitude], [max_latitude, max_longitude]])
                    else:
                        st.error("No data found for the entered Postal Code (PLZ).")
                    
                except (TypeError, ValueError) as e:
                    st.error(e)
    
        else:
            # Create a color map for Numbers
            color_map = LinearColormap(colors=['yellow', 'red'], vmin=dframe1['Number'].min(), vmax=dframe1['Number'].max())
    
            # Add polygons to the map for Charging Stations
            for idx, row in dframe1.iterrows():
                popup = f"PLZ: {row['PLZ']}, Number: {row['Number']}"
                style = lambda x, color=color_map(row['Number']): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                }
                folium.GeoJson(row['geometry'], style_function=style, tooltip=popup).add_to(m)
    
            # Highlight the searched Postal Code if a valid PLZ is found
            if search_button:
                try:
                    session = SessionLocal()
                    postal_code = PostalCode(search_query)  
                    service=ChargingStationService(ChargingStationRepository(session))
                    charging_stations=service.find_stations_by_postal_code(postal_code)
                    latitudes = []
                    longitudes = []
                    if charging_stations:
                        for station in charging_stations:
                            longitude=float(station.longitude.replace(",", "."))
                            latitude=float(station.latitude.replace(",", "."))
                            latitudes.append(latitude)
                            longitudes.append(longitude)
                            power_category, color = get_power_category_and_color(station.power_charging_dev)
                            popup_content = f"""
                            <div style="font-size: 14px;">
                            <h4 style="color: #007bff;">Charging Station Information</h4>
                            <strong>Street:</strong> {station.street}<br>
                            <strong>District:</strong> {station.district}<br>
                            <strong>Location:</strong> {station.location}<br>
                            <strong>Power Charging Device:</strong> {station.power_charging_dev} kW<br>
                            <strong>Charging Device Type:</strong> {station.type_charging_device}<br>
                            <strong>Operator:</strong> {station.operator}<br>
                            <strong>Power Category:</strong> {power_category}<br><br>
                            <p style="color: #888; font-size: 12px;">Click on the marker for more details.</p>
                            </div>
                            """

                            folium.Marker(
                                location=[latitude, longitude],
                                popup=folium.Popup(popup_content, max_width=300),
                                icon=folium.Icon(color=color, icon='cloud')
                            ).add_to(m)

                        min_latitude=min(latitudes)
                        min_longitude=min(longitudes)
                        max_latitude=max(latitudes)
                        max_longitude=max(longitudes)
                        m.fit_bounds([[min_latitude, min_longitude], [max_latitude, max_longitude]])
                    else:
                        st.error("No data found for the entered Postal Code (PLZ).")
                    
                except (TypeError, ValueError) as e:
                    st.error(e)
    
        # Add color map to the map
        color_map.add_to(m)
        
        # Render the map
        folium_static(m, width=800, height=600)

    elif choice == "Report Malfunction":
        st.write("Report Malfunction")
    







