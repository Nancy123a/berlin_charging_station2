import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import pytest
from sqlalchemy import create_engine
from database.database import Base
from sqlalchemy.orm import sessionmaker
from src.register_context.domain.entities.admin import Admin
from src.report_context.domain.entities.notification import Notification
from src.register_context.domain.entities.users import User
from src.register_context.domain.entities.csoperator import CSOperator
from src.search_context.domain.entities.chargingstation import ChargingStation
from src.report_context.domain.entities.report import Report
from sqlalchemy.exc import IntegrityError
from src.report_context.infrastructure.repositories.NotificationRepository import NotificationRepository
from src.report_context.application.services.NotificationService import NotificationService
from src.report_context.domain.events.NotificationCreateEvent import NotificationCreateEvent
      
@pytest.fixture
def db_session():
    """Create a new database session for each test."""
    
    # Set up in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')  # Or point to your test database
    print(Base.metadata.tables)
    Base.metadata.create_all(engine)  # Create tables

    # Session factory
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # ADDING SAMPLE DATA
    session.add(User(user_id=1, username="user_user", password="SecureUserPassword1@"))
    session.add(User(user_id = 2, username="user_user2", password="SecureUserPassword2@"))
    session.commit()

    # Provide the session to the test
    yield session

    # Rollback and close session after each test
    session.rollback()
    session.close()
    
    Base.metadata.drop_all(bind=engine)  # Clean up after test
    
def test_notification_creation(db_session):
    service = NotificationService(NotificationRepository(db_session))
    
    result = service.create_notifications([1, 2, 1], "Notification Content")
    
    assert isinstance(result, NotificationCreateEvent)
    assert result.success == True
    
def test_notification_creation_failure(db_session):
    service = NotificationService(NotificationRepository(db_session))
    
    try:
        service.create_notifications([1], None)
        assert False, "Expected IntegrityError"
    except IntegrityError as e:
        pass
      
def test_get_notifications_by_user_id(db_session):
    service = NotificationService(NotificationRepository(db_session))
    
    test_notification_creation(db_session)
    
    # USER 1
    notifications_result = service.get_notifications_by_user_id(1)
    assert len(notifications_result.notifications) == 2
    assert notifications_result.success == True
    
    # USER 2
    notifications_result = service.get_notifications_by_user_id(2)
    assert len(notifications_result.notifications) == 1
    assert notifications_result.success == True
    
    # USER 3 (No User with ID 3)
    notifications_result = service.get_notifications_by_user_id(3)
    assert len(notifications_result.notifications) == 0
    assert notifications_result.success == True