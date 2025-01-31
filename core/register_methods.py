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

project_root = Path(os.getcwd()).resolve().parent 
sys.path.append(str(project_root))

from sqlalchemy import create_engine,inspect
from sqlalchemy.orm import sessionmaker
from database.database import SessionLocal,engine,Base

from src.register_context.infrastructure.repositories.UserRepository import UserRepository
from src.register_context.application.services.UserService import UserService
from src.register_context.domain.events.UserLoginEvent import UserLoginEvent
from src.register_context.domain.events.UserCreatedEvent import UserCreatedEvent
from src.register_context.domain.events.UserNotFoundEvent import UserNotFoundEvent
from src.register_context.domain.entities.users import User

from src.register_context.infrastructure.repositories.AdminRepository import AdminRepository
from src.register_context.application.services.AdminService import AdminService
from src.register_context.domain.events.AdminCreatedEvent import AdminCreatedEvent
from src.register_context.domain.events.AdminLoginEvent import AdminLoginEvent
from src.register_context.domain.events.AdminNotFoundEvent import AdminNotFoundEvent
from src.register_context.domain.entities.admin import Admin


from src.register_context.infrastructure.repositories.CSOperatorRepository import CSOperatorRepository
from src.register_context.application.services.CSOperatorService import CSOperatorService
from src.register_context.domain.events.CSOperatorLoginEvent import CSOperatorLoginEvent
from src.register_context.domain.events.CSOperatorCreatedEvent import CSOperatorCreatedEvent
from src.register_context.domain.events.CSOperatorNotFoundEvent import CSOperatorNotFoundEvent
from src.register_context.domain.entities.csoperator import CSOperator

from src.search_context.domain.entities.chargingstation import ChargingStation

from src.register_context.domain.value_objects.password import Password


def inspect_and_create_tables():
    table_names = ['chargingstation','user', 'admin','csoperators','report']  # Table names to check
    inspector = inspect(engine)
    
    for table_name in table_names:
        print(table_name)
        if table_name not in inspector.get_table_names():
            print('TABLE IS',table_name)
            Base.metadata.create_all(engine)  # Create all tables defined in Base

    # Get a list of table names
    existing_tables = inspector.get_table_names()
    print('EXXXXXISTING',existing_tables)

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
                password=Password(password)
                if role=="user":
                    user_repository = UserRepository(SessionLocal())
                    user_service = UserService(user_repository)
                        
                    # Register the user and get the event
                    event = user_service.login_user(username, password.value)
                        
                    if isinstance(event, UserLoginEvent):
                        return role
                    elif isinstance(event, UserNotFoundEvent):
                        st.error("Either you didn't register, or your username and password are incorrect")
                elif role=="admin":
                    admin_repository = AdminRepository(SessionLocal())
                    admin_service = AdminService(admin_repository)
                        
                    # Register the user and get the event
                    event = admin_service.login_admin(username, password.value)
                        
                    if isinstance(event, AdminLoginEvent):
                        return role
                    elif isinstance(event, AdminNotFoundEvent):
                        st.error("Either you didn't register, or your username and password are incorrect")
                elif role=="csoperator":
                    csoperator_repository = CSOperatorRepository(SessionLocal())
                    csoperator_service = CSOperatorService(csoperator_repository)
                        
                    # Register the user and get the event
                    event = csoperator_service.login_csoperator(username, password.value)
                        
                    if isinstance(event, CSOperatorLoginEvent):
                        return role
                    elif isinstance(event, CSOperatorNotFoundEvent):
                        st.error("Either you didn't register, or your username and password are incorrect")
                
            except (TypeError, ValueError) as e:
                st.error(e)
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
                        if role=="user":
                             user_repository = UserRepository(SessionLocal())
                             user_service = UserService(user_repository)
                        
                             # Register the user and get the event
                             event = user_service.register_user(new_username, new_password)
                        
                             if isinstance(event, UserCreatedEvent):
                                 st.success('Horayyy!! You have successfully registered')
                             elif isinstance(event, UserNotFoundEvent):
                                 st.error('Username already exists. Please enter a different username')
                        elif role=="admin":
                            admin_repository = AdminRepository(SessionLocal())
                            admin_service = AdminService(admin_repository)
                        
                            # Register the user and get the event
                            event = admin_service.register_admin(new_username, new_password)
                        
                            if isinstance(event, AdminCreatedEvent):
                                st.success('Horayyy!! You have successfully registered')
                            elif isinstance(event, AdminNotFoundEvent):
                                st.error('Username already exists. Please enter a different username')
                        else:
                            csoperator_repository = CSOperatorRepository(SessionLocal())
                            csoperator_service = CSOperatorService(csoperator_repository)
                        
                            # Register the user and get the event
                            event = csoperator_service.register_csoperator(new_username, new_password)
                        
                            if isinstance(event, CSOperatorCreatedEvent):
                                st.success('Horayyy!! You have successfully registered')
                            elif isinstance(event, CSOperatorNotFoundEvent):
                                st.error('Username already exists. Please enter a different username')
                    
                else:
                    st.error(f"Please enter the same password")
            except (TypeError, ValueError) as e:
                st.error(e)





