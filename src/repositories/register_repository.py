import sys
import os

# Get the absolute paths to f1 and f2 directories
domain_directory = os.path.abspath(os.path.join(os.getcwd(), '..', '..', 'domain'))
repository_directory = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))

# Add both directories to sys.path
sys.path.append(domain_directory)  # Add f1 to sys.path
sys.path.append(repository_directory)  # Add f2 to sys.path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from src.domain.value_objects.password import Password  # Correct relative import
from src.sqldatabase.hub.users import User
from src.sqldatabase.hub.admin import Admin
from src.sqldatabase.hub.csoperator import CSOperator
from .register_interface import IRegisterRepository

class RegisterRepository(IRegisterRepository):
    def __init__(self, session: Session):
        """Initialize the repository with a SQLAlchemy session."""
        self.session = session

    def register_user(self, password: Password, username: str) -> bool:
        """Register a user with a given password and username."""
        existing_user = self.session.query(User).filter_by(username=username).first()
        if existing_user:
            return False  # User already exists, registration failed
        ## create new user
        new_user = User(username=username, password=password.value)  # Convert password to string if needed
        # Add the user to the session and commit to the database
        self.session.add(new_user)
        self.session.commit()

        return True

    
    def register_admin(self, password: Password, username: str) -> bool:
        """Register an admin with a given password and username."""
        existing_admin = self.session.query(Admin).filter_by(username=username).first()
        if existing_admin:
            return False  # User already exists, registration failed
        ## create new admin
        new_admin = Admin(username=username, password=password.value,number_reports_assigned=0)  # Convert password to string if needed
        # Add the user to the session and commit to the database
        self.session.add(new_admin)
        self.session.commit()

        return True
    
    def register_csoperator(self, password: Password, username: str) -> bool:
        """Register a charging station operator with a given password and username."""
        existing_csoperator = self.session.query(CSOperator).filter_by(username=username).first()
        if existing_csoperator:
            return False  # User already exists, registration failed
        ## create new csoperator
        new_csoperator = CSOperator(username=username, password=password.value,number_reports_assigned=0)  # Convert password to string if needed
        # Add the user to the session and commit to the database
        self.session.add(new_csoperator)
        self.session.commit()

        return True

    def login_user(self, password: Password, username: str) -> bool:
        existing_user = self.session.query(User).filter_by(username=username,password=password.value).first()
        if not existing_user:
            return False
        return True

    def login_admin(self, password: Password, username: str) -> bool:
        existing_admin = self.session.query(Admin).filter_by(username=username,password=password.value).first()
        if not existing_admin:
            return False
        return True

    def login_csoperator(self, password: Password, username: str) -> bool:
        existing_csoperator = self.session.query(CSOperator).filter_by(username=username,password=password.value).first()
        if not existing_csoperator:
            return False
        return True
        












            