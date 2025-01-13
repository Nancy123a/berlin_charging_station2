import pandas                        as pd
import geopandas                     as gpd
import core.HelperTools              as ht

import folium
# from folium.plugins import HeatMap
import streamlit as st
from streamlit_folium import folium_static

import sys
from pathlib import Path
import os

project_root = Path(os.getcwd()).resolve().parent  # Adjust .parent if needed
sys.path.append(str(project_root))

from sqlalchemy import create_engine,inspect
from sqlalchemy.orm import sessionmaker
from src.sqldatabase.database import SessionLocal,engine,Base
from src.domain.value_objects.password import Password
from src.repositories.register_repository import RegisterRepository
from src.domain.services.register_service import RegisterService
from src.sqldatabase.hub.users import User
from src.sqldatabase.hub.admin import Admin
from src.sqldatabase.hub.csoperator import CSOperator


def inspect_and_create_tables():
    table_names = ['users', 'admins', 'csoperator']  # Table names to check
    inspector = inspect(engine)
    
    for table_name in table_names:
        print(table_name)
        if table_name not in inspector.get_table_names():
            print('creating table')
            Base.metadata.create_all(engine)  # Create all tables defined in Base

    # Get a list of table names
    existing_tables = inspector.get_table_names()

    print("Existing tables in the database:")
    for table in existing_tables:
        print(table)

def register_login():
    
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Select Option", menu)

    if choice == "Login":
        st.subheader("Login Form")
        
        # Create login form
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        role = st.selectbox("Select Role", ["user", "admin", "csoperator"])
        
        if st.button("Login"):
            try:
                password_=Password(password)
                session=SessionLocal()
                service=RegisterService(RegisterRepository(session))
                registered=service.login(password_,username,role)
                if not registered:
                    st.error("Either you didn't register, or your username and password are incorrect")
                else:
                    return role
            except (TypeError, ValueError) as e:
                st.error(e)
    
    elif choice == "Register":
        st.subheader("Registration Form")

        # Create registration form
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type='password')
        confirm_password=st.text_input("Confirm Password",type="password")
        role = st.selectbox("Select Role", ["user", "admin", "csoperator"])

        if st.button("Register"):
            try:
                password=Password(new_password)
                if password.value==confirm_password:
                    if new_username=="":
                        st.error("Please enter your username")
                    else:
                        session=SessionLocal()
                        service=RegisterService(RegisterRepository(session))
                        registered=service.register_user_admin_csoperator(password,new_username,role)
                        if not registered:
                            st.error('Username already exists. Please enter a different username')
                        else:
                            st.success('Horayyy!! You have successfully registered')
                else:
                    st.error(f"Please enter the same password")
            except (TypeError, ValueError) as e:
                st.error(e)





