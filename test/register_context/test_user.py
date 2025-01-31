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
from src.register_context.domain.entities.users import User

# Helper functions to interact with the database
def create_user_in_db(db_session, user):
    """Create a new user in the database from the Users dataclass."""
    db_user = User(username=user.username, password=user.password)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user

def get_user_by_username(db_session, username: str):
    """Fetch a user from the database by username."""
    return db_session.query(User).filter(User.username == username).first()

def get_user_by_id(db_session, user_id: int):
    """Fetch a user from the database by user ID."""
    return db_session.query(User).filter(User.user_id == user_id).first()

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

def test_create_user(db_session):
    """Test creating a user in the database."""
    new_user = User(username="test_user_1", password="Securepassword1@")  # Unique username
    created_user = create_user_in_db(db_session, new_user)
    assert created_user.username == "test_user_1"
    assert created_user.password == "Securepassword1@"

def test_get_user_by_id(db_session):
    """Test fetching a user from the database by ID."""
    new_user = User(username="test_user_2", password="Securepassword1@")  # Unique username
    created_user = create_user_in_db(db_session, new_user)
    fetched_user = get_user_by_id(db_session, created_user.user_id)
    assert fetched_user is not None
    assert fetched_user.username == "test_user_2"
    assert fetched_user.password == "Securepassword1@"

def test_get_user_by_username(db_session):
    """Test fetching a user from the database by username."""
    new_user = User(username="test_user_3", password="Securepassword1@")  # Unique username
    created_user = create_user_in_db(db_session, new_user)
    
    # Fetch the user by username
    fetched_user = get_user_by_username(db_session, created_user.username)
    
    # Assertions to verify the fetched user
    assert fetched_user is not None
    assert fetched_user.username == "test_user_3"
    assert fetched_user.password == "Securepassword1@"

def test_create_user_with_duplicate_username(db_session):
    """Test trying to create a user with the same username twice."""
    # Create first user
    new_user = User(username="duplicate_user", password="Securepassword1@")
    create_user_in_db(db_session, new_user)

    # Attempt to create a second user with the same username
    duplicate_user = User(username="duplicate_user", password="AnotherPassword2@")
    
    # Expecting an IntegrityError due to unique constraint on the username column
    with pytest.raises(ValueError):
        create_user_in_db(db_session, duplicate_user)
