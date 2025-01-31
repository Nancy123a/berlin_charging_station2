import pytest
import sys
from pathlib import Path
import os
from sqlalchemy.exc import IntegrityError  # For handling constraint violation error

project_root = Path(os.getcwd()).resolve().parent  # Adjust .parent if needed
sys.path.append(str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.sqldatabase.database import Base, SessionLocal
from src.sqldatabase.hub.csoperator import CSOperator  # Assuming you have this model in csoperator.py

# Helper functions to interact with the database
def create_cs_operator_in_db(db_session, operator):
    """Create a new CSOperator in the database."""
    db_operator = CSOperator(username=operator.username, password=operator.password, number_reports_assigned=operator.number_reports_assigned)
    db_session.add(db_operator)
    db_session.commit()
    db_session.refresh(db_operator)
    return db_operator

def get_cs_operator_by_username(db_session, username: str):
    """Fetch a CSOperator from the database by username."""
    return db_session.query(CSOperator).filter(CSOperator.username == username).first()

def get_cs_operator_by_id(db_session, cs_operator_id: int):
    """Fetch a CSOperator from the database by cs_operator_id."""
    return db_session.query(CSOperator).filter(CSOperator.cs_operator_id == cs_operator_id).first()

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

def test_create_cs_operator(db_session):
    """Test creating a CSOperator in the database."""
    new_operator = CSOperator(username="operator_user", password="SecureOperatorPassword1@", number_reports_assigned=10)
    created_operator = create_cs_operator_in_db(db_session, new_operator)
    assert created_operator.username == "operator_user"
    assert created_operator.password == "SecureOperatorPassword1@"
    assert created_operator.number_reports_assigned == 10

def test_get_cs_operator_by_id(db_session):
    """Test fetching a CSOperator from the database by cs_operator_id."""
    new_operator = CSOperator(username="operator_user_2", password="SecureOperatorPassword2@", number_reports_assigned=8)
    created_operator = create_cs_operator_in_db(db_session, new_operator)
    fetched_operator = get_cs_operator_by_id(db_session, created_operator.cs_operator_id)
    assert fetched_operator is not None
    assert fetched_operator.username == "operator_user_2"
    assert fetched_operator.password == "SecureOperatorPassword2@"
    assert fetched_operator.number_reports_assigned == 8

def test_get_cs_operator_by_username(db_session):
    """Test fetching a CSOperator from the database by username."""
    new_operator = CSOperator(username="operator_user_3", password="SecureOperatorPassword3@", number_reports_assigned=12)
    created_operator = create_cs_operator_in_db(db_session, new_operator)
    
    # Fetch the operator by username
    fetched_operator = get_cs_operator_by_username(db_session, created_operator.username)
    
    # Assertions to verify the fetched operator
    assert fetched_operator is not None
    assert fetched_operator.username == "operator_user_3"
    assert fetched_operator.password == "SecureOperatorPassword3@"
    assert fetched_operator.number_reports_assigned == 12

def test_create_cs_operator_with_duplicate_username(db_session):
    """Test trying to create a CSOperator with the same username twice."""
    # Create the first operator
    new_operator = CSOperator(username="duplicate_operator", password="SecureOperatorPassword4@", number_reports_assigned=5)
    create_cs_operator_in_db(db_session, new_operator)

    # Attempt to create a second operator with the same username
    duplicate_operator = CSOperator(username="duplicate_operator", password="AnotherOperatorPassword@", number_reports_assigned=2)
    
    # Expecting an IntegrityError due to unique constraint on the username column
    with pytest.raises(TypeError):
        create_cs_operator_in_db(db_session, duplicate_operator)
