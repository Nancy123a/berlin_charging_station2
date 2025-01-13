import sys
import os
import pandas as pd
from core import register_methods as register
from core import methods as m1
from config import pdict
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def main():
    if "logged_in" not in st.session_state:
        # Initialize session state
        st.session_state.logged_in = False
        st.session_state.role = None  # Add role to session state

    if st.session_state.logged_in:
        after_registration(st.session_state.role)
    else:
        register.inspect_and_create_tables()
        role= register.register_login()
        if not role==None:
            st.session_state.logged_in = True
            st.session_state.role = role  # Save role in session state
            st.rerun()  # Refresh the app to show the new state


def after_registration(role):

    # Load datasets
    df_geodat_plz = pd.read_csv(
        os.path.join(os.getcwd(), 'datasets', 'geodata_berlin_plz.csv'), delimiter=';'
    )

    df_lstat = pd.read_csv(
        os.path.join(os.getcwd(), 'datasets', 'Ladesaeulenregister.csv'),
        delimiter=';',
        low_memory=False
    )
    df_lstat = df_lstat[df_lstat['Bundesland'] == 'Berlin']
    df_lstat2 = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    gdf_lstat3 = m1.count_plz_occurrences(df_lstat2)

    df_residents = pd.read_csv(
        os.path.join(os.getcwd(), 'datasets', 'plz_einwohner.csv'), delimiter=','
    )
    gdf_residents2 = m1.preprop_resid(df_residents, df_geodat_plz, pdict)

    # Generate the Streamlit visualization
    m1.make_streamlit_electric_Charging_resid(df_lstat,gdf_lstat3, gdf_residents2,role)


if __name__ == '__main__':
    main()
