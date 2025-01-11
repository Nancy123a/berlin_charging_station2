Electric mobility plays a crucial role in reducing greenhouse gas emissions. As the number of electric vehicles in Berlin continues to grow, the demand for electric charging stations rises correspondingly. This analysis focuses on evaluating the demand for electric charging stations in Berlin to support the city's transition to sustainable transportation.

The Streamlit application: https://electricmobilityberlin-macl9yhkzzjgq7utshfaph.streamlit.app/

Code Documentation:
Program:

Data frames:

1- df_geodata_plz: contain geographical information related to postal code areas (PLZ) in Berlin. It has 2 columns: 

    - PLZ: Represents the postal code (Postleitzahl) of various areas in Berlin
    
    - geometry: Contains geometrical data defining the shape and boundaries of each postal code area (stored as polygon)
    
2-  df_lstat: Contain detailed registry of electric vehicle charging stations. 

    - Location Information:
    
        - Betreiber: Operator of the charging station
        
        - Straße, Hausnummer, Adresszusatz, Postleitzahl, Ort: Address details of the charging station, including street name, house number, additional address info, postal code, and city/town.
        
        - Bundesland: Federal state in Germany where the station is located.
        
        - Kreis/kreisfreie Stadt: District or district-free city where the station is situated.
        
    - Geographical Coordinates:
    
        - Breitengrad: Latitude of the charging station's location.
        
        - Längengrad: Longitude of the charging station's location.
        
    - Station and Charging Details:
    
        - Inbetriebnahmedatum: Date the charging station was put into operation.
        
        - Nennleistung Ladeeinrichtung [kW]: Nominal power output of the charging facility, measured in kilowatts (kW).
        
        - Art der Ladeeinrichung: Type of charging infrastructure (e.g., fast charger, standard charger).
        
        - Anzahl Ladepunkte: Number of charging points available at the station.
        
    - Connector and Power Specifications:
    
        - Steckertypen1, Steckertypen2, etc.: Types of charging connectors (e.g., Type 2, CCS, CHAdeMO).
        
        - P1 [kW], P2 [kW], etc.: Power output for each connector type.
        
        - Public Key1, Public Key2, etc.: Likely identifiers or metadata for the connectors.
        
3- df_residents: provide demographic and geographical information associated with postal codes in Berlin

    - plz: The postal code (Postleitzahl) serving as a unique identifier for specific areas.
    
    - note: Likely includes additional notes or remarks about the postal code area (e.g., administrative or regional designations).
    
    - einwohner: The population count for the corresponding postal code area. This provides insights into how many people live in each region.
    
    - qkm: The area of the postal code region in square kilometers. Useful for understanding population density when combined with the einwohner column.
    
    - lat, long: The geographical coordinates (latitude and longitude) representing the approximate central location of the postal code area.

methods.py:

1- preprop_lstat(dfr, dfg, pdict): designed to preprocess data from the Ladesaeulenregister.csv dataset, focusing on electric vehicle charging stations, and combine it with geographical data. It performs data cleaning, transformation, and filtering to prepare the dataset for further analysis, particularly for the city of Berlin. The parameters are:

    - dfr: The input DataFrame containing data from Ladesaeulenregister.csv.
    
    - dfg: The input DataFrame containing geographical data (e.g., postal code shapes and boundaries).
    
    - pdict: A parameter dictionary that likely contains configuration or metadata required for further processing.
    
It returns ret: A processed and combined DataFrame that includes charging station data filtered for Berlin, augmented with geographical data.

2- count_plz_occurrences(df_lstat2): function calculates the number of electric vehicle charging stations in each postal code (PLZ) from a given dataset. Additionally, it retains the geographical geometry associated with each postal code for mapping or spatial analysis.

    - df_lstat2: same as ret
    
It returns result_df A DataFrame grouped by postal code (PLZ), containing with the following columns: PLZ: The postal code, Number: The count of charging stations in each postal code, geometry: The geographical representation for each postal code.

3- preprop_resid(dfr, dfg, pdict) function preprocesses population data from the plz_einwohner.csv dataset and integrates it with geographical data for further analysis. The function focuses on cleaning and transforming the data, particularly for postal code areas, while preparing it for spatial visualization and analysis. dfr is dataframe that contain information about demographics in berlin. It returns ret which is a processed and enriched DataFrame that includes population data (Einwohner) and geographical information for postal code areas within the range of interest.

4- sort_by_plz_add_geometry(dfr, dfg, pdict): prepares a DataFrame for geospatial analysis by sorting it by postal codes (PLZ), merging it with geographical data, and converting the geometry column into a geospatial format. Note that dfr can be the electric charging stations or the residents dataframe.

5- make_streamlit_electric_Charging_resid(dfr1, dfr2) generates an interactive Streamlit app that displays heatmaps of either electric charging stations or resident populations in Berlin, based on postal code areas (PLZ). The function uses folium for map visualization and allows the user to toggle between viewing charging stations or resident data. 

    - dfr1: A DataFrame containing data on electric charging stations, including postal code (PLZ), number of charging stations per postal code, and geometries.
    
    - dfr2: A DataFrame containing population data, including postal code (PLZ), number of residents (Einwohner), and geometries for each postal code area.
    
It returns None. 

HelperTools.py:

- timer(func): The timer decorator function measures and prints the execution time of any function it wraps. It calculates how long the decorated function takes to run and prints the duration along with the function's documentation (docstring).

Interpretation of results:

A Streamlit application is created that displays a map of Berlin divided into different postal code areas (PLZ). Users can toggle between two views: one showing the number of residents in each area and the other displaying the number of available charging stations. The number of charging stations ranges from 1 to 95, while the number of residents varies from 139 to 35,353.

For both views, the color scale starts with a light yellow for areas with lower values, becoming progressively darker until reaching a dark orange color for areas with higher numbers of residents or charging stations. This color gradient helps users easily visualize the density of both residents and charging stations across the city.


Question: Analyze both geovisualizations: Where do you see demand for additional electric charging stations?

Answer:
High-demand postal code areas (PLZ) for electric vehicle (EV) stations were identified by analyzing the color intensity on the charging station map (light yellow) and the population map (medium orange or darker). A threshold was set for the number of residents (greater than 15,000) and the number of charging stations (fewer than 11). After merging the two datasets, gdf_lstat3 and gdf_residents2, we applied these thresholds to filter for areas with both high population and low charging station availability.

Based on this criterion, the postal codes (PLZ) with the highest demand for EV charging stations are:

| Numberr  | Number | Einwohner |
|----------|--------|-----------|
| 10119.0  | 6      | 16363     |
| 10315.0  | 6      | 28442     |
| 10318.0  | 4      | 22187     |
| 10319.0  | 5      | 22951     |
| 10367.0  | 5      | 18902     |
| 10369.0  | 6      | 19115     |
| 10435.0  | 6      | 15359     |
| 10437.0  | 9      | 27821     |
| 10551.0  | 5      | 16424     |
| 10715.0  | 6      | 15464     |
| 10961.0  | 9      | 17874     |
| 10997.0  | 10     | 23800     |
| 12045.0  | 5      | 15523     |
| 12049.0  | 2      | 18890     |
| 12051.0  | 8      | 22413     |
| 12059.0  | 7      | 16059     |
| 12105.0  | 9      | 22534     |
| 12107.0  | 6      | 19741     |
| 12157.0  | 5      | 18385     |
| 12161.0  | 8      | 16654     |
| 12169.0  | 8      | 16524     |
| 12279.0  | 2      | 16381     |
| 12305.0  | 3      | 20742     |
| 12349.0  | 5      | 21692     |
| 12353.0  | 4      | 31768     |
| 12355.0  | 5      | 27263     |
| 12557.0  | 8      | 21494     |
| 12559.0  | 2      | 17643     |
| 12679.0  | 6      | 25777     |
| 12685.0  | 8      | 18578     |
| 12687.0  | 6      | 17992     |
| 13051.0  | 5      | 21820     |
| 13057.0  | 9      | 16106     |
| 13086.0  | 9      | 24110     |
| 13127.0  | 6      | 19255     |
| 13187.0  | 8      | 30146     |
| 13189.0  | 4      | 25951     |
| 13353.0  | 10     | 24259     |
| 13359.0  | 4      | 22161     |
| 13407.0  | 4      | 24022     |
| 13409.0  | 7      | 26581     |
| 13435.0  | 4      | 17011     |
| 13439.0  | 1      | 19016     |
| 13469.0  | 9      | 16156     |
| 13583.0  | 8      | 20761     |
| 13589.0  | 3      | 21103     |
| 13591.0  | 6      | 26815     |
| 13593.0  | 10     | 20185     |
| 13595.0  | 6      | 19966     |
| 13627.0  | 2      | 17126     |
| 14167.0  | 10     | 15485     |
| 14193.0  | 3      | 15505     |
