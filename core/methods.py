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
from database.database import SessionLocal,engine,Base
from src.search_context.domain.value_objects.postal_code import PostalCode
from src.search_context.domain.entities.chargingstation import ChargingStation
from src.search_context.application.services.ChargingStationService import ChargingStationService
from src.search_context.infrastructure.repositories.ChargingStationRepository import ChargingStationRepository
import database.import_database as db
from geopy.exc import GeocoderTimedOut

from src.report_context.domain.entities.report import Report
from src.report_context.application.services.ReportService import ReportService
from src.report_context.infrastructure.repositories.ReportRepository import ReportRepository
from src.register_context.infrastructure.repositories.AdminRepository import AdminRepository
from src.register_context.application.services.AdminService import AdminService
from src.register_context.infrastructure.repositories.CSOperatorRepository import CSOperatorRepository
from src.register_context.application.services.CSOperatorService import CSOperatorService
import time
from src.register_context.domain.entities.csoperator import CSOperator
from src.register_context.domain.entities.admin import Admin
from folium import Popup, Marker
from src.search_context.domain.events.PostalCodeFoundEvent import PostalCodeFoundEvent
from src.search_context.domain.events.PostalCodeNotFoundEvent import PostalCodeNotFoundEvent
from core import register_methods as register
from src.report_context.application.services.NotificationService import NotificationService
from src.report_context.infrastructure.repositories.NotificationRepository import NotificationRepository
from src.register_context.application.services.UserService import UserService
from src.register_context.infrastructure.repositories.UserRepository import UserRepository
from src.search_context.domain.events.StationNotFoundEvent import StationNotFoundEvent
from src.search_context.domain.events.StationFoundEvent import StationFoundEvent
from src.report_context.domain.aggregate.ReportAggregateService import ReportAggregateService
from src.report_context.domain.events.ReportAlreadyExistsEvent import ReportAlreadyExistsEvent
from src.report_context.domain.events.ReportCreateFailedEvent import ReportCreateFailedEvent
from src.report_context.domain.events.ReportCreateEvent import ReportCreateEvent
from src.report_context.domain.events.ReportUpdateEvent import ReportUpdateEvent
from src.report_context.domain.value_objects.report_description import ReportDescription
from src.report_context.domain.value_objects.report_severity import ReportSeverity
from src.report_context.domain.value_objects.report_type import ReportType

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
    service=ChargingStationService(ChargingStationRepository(SessionLocal()))
    isempty=service.is_table_empty()
    if isempty:
        db.import_charging_stations_from_csv(df)


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
def make_streamlit_electric_Charging_resid(df, dfr1, dfr2, role, user_id):
    """Makes Streamlit App with Heatmap of Electric Charging Stations and Residents"""
    inspect_db(df)

    # Define menu options based on role
    menu = {
        "user": ["Search Station", "Report Malfunction", "Notifications","Logout"],
        "admin": ["Search Station", "Manage Malfunction Report", "Logout"],
        "csoperator": ["Search Station", "Resolve Malfunction Report","Logout"]
    }
    
    choice = st.sidebar.selectbox("Select Option", menu.get(role, []))
    
    # REPORT REPOSITORY & SERVICE
    report_repository = ReportRepository(SessionLocal())
    report_service = ReportService(report_repository)
    
    # ADMIN REPOSITORY & SERVICE
    admin_repository = AdminRepository(SessionLocal())
    admin_service = AdminService(admin_repository)
    
    # CHARGING STATION REPOSITORY & SERVICE
    chargingstation_repository = ChargingStationRepository(SessionLocal())
    chargingstation_service = ChargingStationService(chargingstation_repository)
    
    # CHARGING STATION OPERATOR REPOSITORY & SERVICE
    csoperator_repository = CSOperatorRepository(SessionLocal())
    csoperator_service = CSOperatorService(csoperator_repository)
    
    # NOTIFICATION REPOSITORY & SERVICE
    notification_repository = NotificationRepository(SessionLocal())
    notification_service = NotificationService(notification_repository)
    
    # USER REPOSITORY & SERVICE
    user_repository = UserRepository(SessionLocal())
    user_service = UserService(user_repository)
    
    # REPORT AGGREGATE REPOSITORY & SERVICE
    report_aggregate_service = ReportAggregateService(user_repository=user_repository, notification_repository=notification_repository, admin_repository=admin_repository, chargingstation_repository=chargingstation_repository,
    report_repository=report_repository,
    csoperator_repository=csoperator_repository)

    if choice=="Logout":
        return "logout"
    
    elif choice == "Search Station":
        st.title('Heatmaps: Electric Charging Stations and Residents')

        # Search Box
        search_query = st.text_input("Enter Postal Code (PLZ) to Search:", "")
        search_button = st.button("Search")

        # Create a radio button for layer selection
        layer_selection = st.radio("Select Layer", ("Residents", "Charging_Stations"))

        # Create a Folium map
        m = folium.Map(location=[52.52, 13.40], zoom_start=10)

        # Function to add data to the map
        def add_layer_to_map(data, color_map, layer_name):
            for idx, row in data.iterrows():
                popup = f"PLZ: {row['PLZ']}, {layer_name}: {row['Number'] if layer_name == 'Charging Stations' else row['Einwohner']}"
                style = lambda x, color=color_map(row['Number'] if layer_name == 'Charging Stations' else row['Einwohner']): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                }
                folium.GeoJson(row['geometry'], style_function=style, tooltip=popup).add_to(m)

        # Create color map for Residents or Charging Stations
        def get_color_map(data, value_column):
            return LinearColormap(colors=['yellow', 'red'], vmin=data[value_column].min(), vmax=data[value_column].max())

        # Handle both Residents and Charging Stations
        if layer_selection == "Residents":
            color_map = get_color_map(dfr2, 'Einwohner')
            add_layer_to_map(dfr2, color_map, "Residents")

        else:  # Charging Stations
            color_map = get_color_map(dfr1, 'Number')
            add_layer_to_map(dfr1, color_map, "Charging Stations")

        # Handle searching for charging stations by postal code
        if search_button:
            try:
                session = SessionLocal()
                event=chargingstation_service.verify_postal_code(search_query)
                if isinstance(event, PostalCodeFoundEvent):
                    charging_station_event = chargingstation_service.find_stations_by_postal_code(event.postal_code)
                    if isinstance(charging_station_event, StationFoundEvent):
                        charging_stations=charging_station_event.stations
                        latitudes, longitudes = [], []
                        for station in charging_stations:
                            latitude = station.charging_station.latitude
                            longitude = station.charging_station.longitude
                            latitudes.append(latitude)
                            longitudes.append(longitude)
        
                            power_category, color = get_power_category_and_color(station.charging_station.power_charging_dev)
                            popup_content = f"""
                            <div style="font-size: 14px;">
                            <h4 style="color: #007bff;">Charging Station Information</h4>
                            <strong>Street:</strong> {station.charging_station.street}<br>
                            <strong>District:</strong> {station.charging_station.district}<br>
                            <strong>Location:</strong> {station.charging_station.location}<br>
                            <strong>Power Charging Device:</strong> {station.charging_station.power_charging_dev} kW<br>
                            <strong>Charging Device Type:</strong> {station.charging_station.type_charging_device}<br>
                            <strong>Operator:</strong> {station.charging_station.operator}<br>
                            <strong>Power Category:</strong> {power_category}<br><br>
                            <p style="color: #888; font-size: 12px;">Click on the marker for more details.</p>
                            </div>
                            """
                            Marker(location=[latitude, longitude],
                                   popup=Popup(popup_content, max_width=300),
                                   icon=folium.Icon(color=color, icon='cloud')).add_to(m)
        
                            m.fit_bounds([[min(latitudes), min(longitudes)], [max(latitudes), max(longitudes)]])
                else:
                    st.error("No data found for the entered Postal Code (PLZ).")

            except (TypeError, ValueError) as e:
                st.error(e)

        # Add color map to the map and render
        color_map.add_to(m)
        folium_static(m, width=800, height=600)

    elif choice == "Report Malfunction":                        
        st.title('Report Station Malfunction')
        
        description = st.text_area("Description")
        severity, severity_label = st.selectbox("Select Severity", [("low", "Low"), ("medium", "Medium"), ("high", "High")], format_func=lambda x: x[1])
        type, type_label = st.selectbox("Select Type", [("hardware", "Hardware"), ("software", "Software"), ("connectivity", "Connectivity")], format_func=lambda x: x[1])
        postal_code = st.text_input("Postal Code")
        
        
        
        try:
            if postal_code:
                postal_code = PostalCode(postal_code).value
                
                searched_stations = chargingstation_service.find_stations_by_postal_code(postal_code)
                
                if isinstance(searched_stations, StationNotFoundEvent) and searched_stations.success:
                    st.error("No data found for the entered Postal Code (PLZ).")
                    station_id = None
                else:
                    station_id, station_id_label  = st.selectbox("Select Station", [(station.charging_station.station_id, 'Station ID: ' + str(station.charging_station.station_id) + ' | Street: ' + station.charging_station.street) for station in searched_stations], format_func=lambda x: x[1])
            
            else:
                station_id = None
                    
            submit_button = st.button("Submit")
            
            if submit_button:
                description = ReportDescription(description).value
                severity = ReportSeverity(severity).value
                type = ReportType(type).value
                
                if not station_id:
                    st.error("Please enter Postal Code and select Station before submitting")
                    return
                        
                report = Report(station_id=station_id, description=description, severity=severity, type=type, user_id=user_id)         
                result = report_aggregate_service.report_malfunction(report)
                
                if isinstance(result, ReportAlreadyExistsEvent):
                    st.error(result.reason)
                elif isinstance(result, ReportCreateFailedEvent):
                    st.error(result.reason)
                elif isinstance(result, ReportCreateEvent):
                    st.success("Malfunction issue report successfully forwarded")
                    
                    time.sleep(2)
                    st.rerun()
            
        except (TypeError, ValueError) as e:
            st.error(e)
    
    elif choice == "Manage Malfunction Report":
        st.title('Manage Malfunction Report')
        
        # Get all reports for logged in admin
        all_reports = report_service.get_reports_by_admin_id(user_id).reports
        
        if not all_reports:
            st.text("No reports found for the logged in admin.")
            return
        
        report_data = [{
            "Report ID": report.report_id,
            "Station ID": str(report.station_id),
            "Street Name": report.chargingstation.street,
            "Postal Code": report.chargingstation.postal_code,
            "Station District": report.chargingstation.district,
            "Description": report.description,
            "Severity": report.severity,
            "Status": report.status,
            "Assigned To": report.csoperator.username if report.csoperator else "NA",
            "Created At": report.created_at,
            "Updated At": report.updated_at
        } for report in all_reports]
        
        st.subheader("All Reports")
        
        report_df = pd.DataFrame(report_data)        
        
        st.dataframe(report_df, hide_index=True)
        
        reports_to_be_forwarded = [report for report in all_reports if report.status == "pending"]
        
        report = st.selectbox("Forward Report to Charging Station Operator", reports_to_be_forwarded, format_func=lambda x: "REPORT ID: " + str(x.report_id) + " | Station ID: " + str(x.station_id))
        
        forward_button = st.button("Forward", disabled=not report)
        
        if forward_button:
            result = report_aggregate_service.forward_report_malfunction(report)
            
            if isinstance(result, ValueError):
                st.error(result)
            elif isinstance(result, ReportUpdateEvent) and result.success:
                st.success("Malfunction issue report successfully forwarded")
                
                time.sleep(2)
                st.rerun()

    elif choice == "Resolve Malfunction Report":
        st.title("Resolve Malfunction Report")
        
        # Get all reports for logged in charging station operator
        all_reports = report_service.get_reports_by_csoperator_id(user_id).reports
        
        if not all_reports:
            st.text("No reports found for the logged in charging station operator.")
            return
        
        report_data = [{
            "Report ID": report.report_id,
            "Station ID": str(report.station_id),
            "Street Name": report.chargingstation.street,
            "Postal Code": report.chargingstation.postal_code,
            "Station District": report.chargingstation.district,
            "Description": report.description,
            "Severity": report.severity,
            "Status": report.status,
            "Created At": report.created_at,
            "Updated At": report.updated_at
        } for report in all_reports]
        
        st.subheader("Fixes to be Done")
        
        report_df = pd.DataFrame(report_data)        
        
        st.dataframe(report_df, hide_index=True)
        
        reports_to_be_resolved = [report for report in all_reports if report.status == "managed"]
        
        report = st.selectbox("Mark as Resolved", reports_to_be_resolved, format_func=lambda x: "REPORT ID: " + str(x.report_id) + " | Station ID: " + str(x.station_id))
        
        # all_reports find report.id
        selected_report = None
        
        for rep in all_reports:
            if report and rep.report_id == report.report_id:
                selected_report = rep
                break
            
        resolve_button = st.button("Resolve", disabled=not selected_report)
        
        if resolve_button:
            result = report_aggregate_service.resolve_report_malfunction(selected_report)
            
            if isinstance(result, ValueError):
                st.error(result)
            elif isinstance(result, ReportUpdateEvent) and result.success:
                st.success("Malfunction issue report successfully resolved")
                
                time.sleep(2)
                st.rerun()
                
    elif choice == "Notifications":
        st.title('Notifications')
        
        # Get all notifications for logged in user
        all_notifications = notification_service.get_notifications_by_user_id(user_id).notifications
        
        if not all_notifications:
            st.text("No notifications found for the logged in user.")
            return
        
        all_notifications = sorted(all_notifications, key=lambda x: x.created_at, reverse=True)
        
        for notification in all_notifications:
            st.write("Created At: ", notification.created_at)
            st.write(notification.content, unsafe_allow_html=True)
            st.html("<hr/>")
        
    return role