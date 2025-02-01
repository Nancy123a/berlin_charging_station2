import pandas as pd
import geopandas as gpd
import core.HelperTools as ht

import folium
import streamlit as st
from streamlit_folium import folium_static

import sys
from pathlib import Path
import os

project_root = Path(os.getcwd()).resolve().parent 
sys.path.append(str(project_root))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from database.database import SessionLocal, engine, Base

from src.register_context.infrastructure.repositories.UserRepository import UserRepository
from src.register_context.application.services.UserService import UserService
from src.register_context.domain.events.UserLoginEvent import UserLoginEvent
from src.register_context.domain.events.UserCreatedEvent import UserCreatedEvent
from src.register_context.domain.events.UserAlreadyExistEvent import UserAlreadyExistEvent
from src.register_context.domain.entities.users import User

from src.register_context.infrastructure.repositories.AdminRepository import AdminRepository
from src.register_context.application.services.AdminService import AdminService
from src.register_context.domain.events.AdminCreatedEvent import AdminCreatedEvent
from src.register_context.domain.events.AdminLoginEvent import AdminLoginEvent
from src.register_context.domain.events.AdminAlreadyExistEvent import AdminAlreadyExistEvent
from src.register_context.domain.entities.admin import Admin

from src.register_context.infrastructure.repositories.CSOperatorRepository import CSOperatorRepository
from src.register_context.application.services.CSOperatorService import CSOperatorService
from src.register_context.domain.events.CSOperatorLoginEvent import CSOperatorLoginEvent
from src.register_context.domain.events.CSOperatorCreatedEvent import CSOperatorCreatedEvent
from src.register_context.domain.events.CSOperatorAlreadyExistEvent import CSOperatorAlreadyExistEvent
from src.register_context.domain.entities.csoperator import CSOperator

from src.search_context.domain.entities.chargingstation import ChargingStation
from src.register_context.domain.value_objects.password import Password
from src.register_context.domain.events.PasswordVerifiedEvent import PasswordVerifiedEvent


def inspect_and_create_tables():
    table_names = ['chargingstation', 'user', 'admin', 'csoperators', 'report', 'notification']  
    inspector = inspect(engine)
    
    for table_name in table_names:
        print(table_name)
        if table_name not in inspector.get_table_names():
            print('Creating TABLE:', table_name)
            Base.metadata.create_all(engine)  

    existing_tables = inspector.get_table_names()
    print('Existing tables:', existing_tables)


def register_login():
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Select Option", menu)

    if choice == "Login":
        st.subheader("Login Form")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        role = st.selectbox("Select Role", ["user", "admin", "csoperator"])

        if st.button("Login"):
            try:
                repository_class = {"user": UserRepository, "admin": AdminRepository, "csoperator": CSOperatorRepository}[role]
                service_class = {"user": UserService, "admin": AdminService, "csoperator": CSOperatorService}[role]
                login_method = {"user": "login_user", "admin": "login_admin", "csoperator": "login_csoperator"}[role]
                event_class = {"user": UserLoginEvent, "admin": AdminLoginEvent, "csoperator": CSOperatorLoginEvent}[role]
                not_found_class = {"user": UserAlreadyExistEvent, "admin": AdminAlreadyExistEvent, "csoperator": CSOperatorAlreadyExistEvent}[role]
                
                repository = repository_class(SessionLocal())
                service = service_class(repository)
                
                event_password = service.verify_password(password)
                if isinstance(event_password, PasswordVerifiedEvent):
                    event = getattr(service, login_method)(username, password)

                    if isinstance(event, event_class):
                        return role, event.user_id if role == "user" else event.sys_admin_id if role == "admin" else event.cs_operator_id
                    elif isinstance(event, not_found_class):
                        st.error("Invalid username or password")
            except (TypeError, ValueError) as e:
                st.error(str(e))

    elif choice == "Register":
        st.subheader("Registration Form")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type='password')
        confirm_password = st.text_input("Confirm Password", type='password')
        role = st.selectbox("Select Role", ["user", "admin", "csoperator"])

        if st.button("Register"):
            if new_password != confirm_password:
                st.error("Passwords do not match")  # ✅ Fixed indentation issue
                return None, None
            
            if not new_username:
                st.error("Please enter a username")
                return None, None

            try:
                repository_class = {"user": UserRepository, "admin": AdminRepository, "csoperator": CSOperatorRepository}[role]
                service_class = {"user": UserService, "admin": AdminService, "csoperator": CSOperatorService}[role]
                register_method = {"user": "register_user", "admin": "register_admin", "csoperator": "register_csoperator"}[role]
                created_class = {"user": UserCreatedEvent, "admin": AdminCreatedEvent, "csoperator": CSOperatorCreatedEvent}[role]
                not_found_class = {"user": UserAlreadyExistEvent, "admin": AdminAlreadyExistEvent, "csoperator": CSOperatorAlreadyExistEvent}[role]

                repository = repository_class(SessionLocal())
                service = service_class(repository)
                
                event_password = service.verify_password(new_password)
                if isinstance(event_password, PasswordVerifiedEvent):
                    event = getattr(service, register_method)(new_username, new_password)
    
                    if isinstance(event, created_class):
                        st.success("Registration successful!")
                        return role, None
                    elif isinstance(event, not_found_class):
                        st.error("Username already exists")
            except (TypeError, ValueError) as e:
                st.error(str(e))

    return None, None  # ✅ Fixed invalid syntax
