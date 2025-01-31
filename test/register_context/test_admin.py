import pytest
import sys
from pathlib import Path
import os
from sqlalchemy.exc import IntegrityError  # Import for handling constraint violation error

project_root = Path(os.getcwd()).resolve().parent.parent  # Adjust .parent if needed
sys.path.append(str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, SessionLocal
from src.register_context.domain.entities.admin import Admin  # Assuming you have this model in admins.py

# Helper functions to interact with the database
def create_admin_in_db(db_session, admin):
    """Create a new admin in the database."""
    db_admin = Admin(username=admin.username, password=admin.password, number_reports_assigned=admin.number_reports_assigned)
    db_session.add(db_admin)
    db_session.commit()
    db_session.refresh(db_admin)
    return db_admin

def get_admin_by_username(db_session, username: str):
    """Fetch an admin from the database by username."""
    return db_session.query(Admin).filter(Admin.username == username).first()

def get_admin_by_id(db_session, sys_admin_id: int):
    """Fetch an admin from the database by sys_admin_id."""
    return db_session.query(Admin).filter(Admin.sys_admin_id == sys_admin_id).first()

@pytest.fixture(scope="module")
def db_session():
    # Set up in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)  # Create all tables

    session = SessionLocal(bind=engine)  # Create session for testing
    yield session
    session.rollback()  # Rollback any changes after test
    session.close()
    Base.metadata.drop_all(bind=engine)  # Clean up after test

def test_create_admin(db_session):
    """Test creating an admin in the database."""
    new_admin = Admin(username="admin_user", password="SecureAdminPassword1@", number_reports_assigned=5)
    created_admin = create_admin_in_db(db_session, new_admin)
    assert created_admin.username == "admin_user"
    assert created_admin.password == "SecureAdminPassword1@"
    assert created_admin.number_reports_assigned == 5

def test_get_admin_by_id(db_session):
    """Test fetching an admin from the database by sys_admin_id."""
    new_admin = Admin(username="admin_user_2", password="SecureAdminPassword2@", number_reports_assigned=3)
    created_admin = create_admin_in_db(db_session, new_admin)
    fetched_admin = get_admin_by_id(db_session, created_admin.sys_admin_id)
    assert fetched_admin is not None
    assert fetched_admin.username == "admin_user_2"
    assert fetched_admin.password == "SecureAdminPassword2@"
    assert fetched_admin.number_reports_assigned == 3

def test_get_admin_by_username(db_session):
    """Test fetching an admin from the database by username."""
    new_admin = Admin(username="admin_user_3", password="SecureAdminPassword3@", number_reports_assigned=8)
    created_admin = create_admin_in_db(db_session, new_admin)
    
    # Fetch the admin by username
    fetched_admin = get_admin_by_username(db_session, created_admin.username)
    
    # Assertions to verify the fetched admin
    assert fetched_admin is not None
    assert fetched_admin.username == "admin_user_3"
    assert fetched_admin.password == "SecureAdminPassword3@"
    assert fetched_admin.number_reports_assigned == 8

def test_create_admin_with_duplicate_username(db_session):
    """Test trying to create an admin with the same username twice."""
    # Create the first admin
    new_admin = Admin(username="duplicate_admin", password="SecureAdminPassword4@", number_reports_assigned=5)
    create_admin_in_db(db_session, new_admin)

    # Attempt to create a second admin with the same username
    duplicate_admin = Admin(username="duplicate_admin", password="AnotherAdminPassword@", number_reports_assigned=2)
    
    # Expecting an IntegrityError due to unique constraint on the username column
    with pytest.raises(TypeError):
        create_admin_in_db(db_session, duplicate_admin)
