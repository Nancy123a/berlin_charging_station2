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
        print("YESSSSSSS ITS EMPTYYYYYY")
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
def make_streamlit_electric_Charging_resid(df,dfr1, dfr2,role):
    """Makes Streamlit App with Heatmap of Electric Charging Stations and Residents"""
    inspect_db(df)
    #chargingstation_repository = ChargingStationRepository(SessionLocal())
    #chargingstation_service = ChargingStationService(chargingstation_repository)
    #charging_stations = chargingstation_service.find_stations_by_postal_code('10559')

    #for station in charging_stations:
     #   st.write(station.charging_station.street)  
    if role=="user":
        menu = ["Search Station", "Report Malfunction","Notifications"]
    elif role=="admin":
        menu = ["Search Station", "Manage Malfunction Report","Notifications"]
    elif role=="csoperator":
        menu = ["Search Station", "Resolve Malfunction Report"]
        
    choice = st.sidebar.selectbox("Select Option",menu)
    
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
            if search_button:
                try:
                    session = SessionLocal()
                    postal_code = PostalCode(search_query)
                    charging_stations = chargingstation_service.find_stations_by_postal_code(postal_code.value)

                    latitudes = []
                    longitudes = []
                    if charging_stations:
                        for station in charging_stations:
                            longitude=station.charging_station.longitude
                            latitude=station.charging_station.latitude
                            latitudes.append(latitude)
                            longitudes.append(longitude)
                            # Get color based on the charging station's power
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
    
               
    
        # Add color map to the map
        color_map.add_to(m)
        
        # Render the map
        folium_static(m, width=800, height=600)

    elif choice == "Report Malfunction":                        
        st.title('Report Station Malfunction')
        
        description = st.text_area("Description")
        severity, severity_label = st.selectbox("Select Severity", [("low", "Low"), ("medium", "Medium"), ("high", "High")], format_func=lambda x: x[1])
        postal_code = st.text_input("Postal Code")
        
        
        try:
            if postal_code:
                postal_code = PostalCode(postal_code).value
                
                searched_stations = chargingstation_service.find_stations_by_postal_code(postal_code)
                
                station_id, station_id_label  = st.selectbox("Select Station", [(station.charging_station.station_id, 'Station ID: ' + str(station.charging_station.station_id) + ' | Street: ' + station.charging_station.street) for station in searched_stations], format_func=lambda x: x[1])
            
            else:
                station_id = None
                    
            submit_button = st.button("Submit")
            
            if submit_button:
                if not description:
                    st.error("Please fill Description")
                elif not severity:
                    st.error("Please select Severity")
                elif not station_id:
                    st.error("Please select Station")
                else:                    
                    # Get the first admin with less than 10 reports assigned
                    all_admins = admin_service.get_all_admins()
                    admin = None
                    for admin in all_admins:
                        if(admin.number_reports_assigned < 10):
                            admin = admin
                            break
                    # If no admin with less than 10 reports is found, get the first admin
                    if not admin:
                        admin = all_admins[0]
                    
                    # Create the report
                    report = Report(station_id=station_id, description=description, severity=severity, user_id=1, admin_id=admin.sys_admin_id)
                    report_service.create_report(report)
                    
                    # Update the number of reports assigned to the admin
                    admin.number_reports_assigned += 1
                    admin_service.update_admin(admin)
                    
                    st.success("Malfunction issue report successfully forwarded")
            
        except (TypeError, ValueError) as e:
            st.error(e)
    
    elif choice == "Manage Malfunction Report":
        st.title('Manage Malfunction Report')
        
        # Get all reports for logged in admin
        all_reports = report_service.get_reports_by_admin_id(1)
        
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
        
        forward_button = st.button("Forward")
        
        if forward_button:
            try: 
                # Get all charging station operators
                all_csoperators = csoperator_service.get_all_csoperators()
                cs_operator = None
                # Get the first operator with less than 10 reports assigned
                for operator in all_csoperators:
                    if(operator.number_reports_assigned < 10):
                        cs_operator = operator
                        break
                # If no operator with less than 10 reports is found, get the first operator
                if not cs_operator:
                    cs_operator = all_csoperators[0]
                
                # Update the report
                report.csoperator = cs_operator
                report.status = "managed"
                report_service.update_report(report)
                
                # Update the charging station operator
                cs_operator.number_reports_assigned += 1
                csoperator_repository.update_csoperator(cs_operator)
                
                st.success("Malfunction issue report successfully forwarded")
                
                time.sleep(2)
                st.rerun()
            except (TypeError, ValueError) as e:
                st.error(e)

    elif choice == "Resolve Malfunction Report":
        st.title("Resolve Malfunction Report")
        
        # Get all reports for logged in charging station operator
        all_reports = report_service.get_reports_by_csoperator_id(1)
        
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
            if rep.report_id == report.report_id:
                selected_report = rep
                break
            
        resolve_button = st.button("Resolve", key=report.report_id)
        
        if resolve_button:
            try: 
                # Update the admin
                admin = selected_report.admin
                admin.number_reports_assigned -= 1
                admin_repository.update_admin(admin)
                
                # Update the charging station operator
                cs_operator = selected_report.csoperator
                cs_operator.number_reports_assigned -= 1
                csoperator_repository.update_csoperator(cs_operator)
                
                # Update the report
                report.status = "resolved"
                report_service.update_report(report)
                
                st.success("Malfunction issue report successfully resolved")
                
                time.sleep(2)
                st.rerun()
            except (TypeError, ValueError) as e:
                st.error(e)

        
    return role