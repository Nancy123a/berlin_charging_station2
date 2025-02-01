import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from datetime import datetime
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
from src.report_context.infrastructure.repositories.ReportRepository import ReportRepository
from src.report_context.domain.events.ReportAlreadyExistsEvent import ReportAlreadyExistsEvent
from src.report_context.domain.events.ReportCreateEvent import ReportCreateEvent
from src.report_context.domain.aggregate.ReportAggregateService import ReportAggregateService
from src.report_context.infrastructure.repositories.NotificationRepository import NotificationRepository
from src.register_context.infrastructure.repositories.UserRepository import UserRepository
from src.register_context.infrastructure.repositories.AdminRepository import AdminRepository
from src.search_context.infrastructure.repositories.ChargingStationRepository import ChargingStationRepository
from src.register_context.infrastructure.repositories.CSOperatorRepository import CSOperatorRepository
from sqlalchemy.exc import IntegrityError
from src.report_context.domain.events.ReportUpdateEvent import ReportUpdateEvent


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
    session.add(Admin(sys_admin_id=1, username="admin_user", password="SecureAdminPassword1@", number_reports_assigned=0))
    session.add(User(user_id=1, username="user_user", password="SecureUserPassword1@"))
    session.add(CSOperator(cs_operator_id=1, username="cs_operator_user", password="SecureCSOperatorPassword1@", number_reports_assigned=0))
    session.add(ChargingStation(station_id=123, postal_code="12345", latitude=52.5200, longitude=13.4050, location="Berlin, Germany", street="Unter den Linden", district="Mitte", federal_state="Berlin", operator="Berlin Charging", power_charging_dev=5, commission_date=datetime.strptime("11.10.2020", "%d.%m.%Y").date(), type_charging_device="Fast", cs_status="active"))
    session.commit()

    # Provide the session to the test
    yield session

    # Rollback and close session after each test
    session.rollback()
    session.close()
    
    Base.metadata.drop_all(bind=engine)  # Clean up after test
    
def test_malfunction_reporting_success(db_session):
    service = ReportAggregateService(ReportRepository(db_session), UserRepository(db_session), NotificationRepository(db_session), AdminRepository(db_session), ChargingStationRepository(db_session), CSOperatorRepository(db_session))
    
    result = service.report_malfunction(Report(station_id=123, description="Report Description", severity="low", type="hardware", user_id=1))
    
    assert isinstance(result, ReportCreateEvent)
    assert result.success == True
    
def test_malfunction_reporting_duplication(db_session):
    test_malfunction_reporting_success(db_session)
    
    service = ReportAggregateService(ReportRepository(db_session), UserRepository(db_session), NotificationRepository(db_session), AdminRepository(db_session), ChargingStationRepository(db_session), CSOperatorRepository(db_session))
    
    result = service.report_malfunction(Report(station_id=123, description="Report Description", severity="low", type="hardware", user_id=1))
    
    assert isinstance(result, ReportAlreadyExistsEvent)
    assert result.exisiting_report.status == "pending"
    assert result.success == False

def test_malfunction_reporting_failure(db_session):
    service = ReportAggregateService(ReportRepository(db_session), UserRepository(db_session), NotificationRepository(db_session), AdminRepository(db_session), ChargingStationRepository(db_session), CSOperatorRepository(db_session))
    
    try:
        service.report_malfunction(Report(station_id=123, description=None, severity="low", type="hardware", user_id=1))
        assert False, "Expected IntegrityError"
    except IntegrityError as e:
        pass
      
def test_forward_report_malfunction(db_session):
    service = ReportAggregateService(ReportRepository(db_session), UserRepository(db_session), NotificationRepository(db_session), AdminRepository(db_session), ChargingStationRepository(db_session), CSOperatorRepository(db_session))
    
    report = Report(report_id=1, station_id=123, description="Report Description", severity="low", type="hardware", user_id=1)
    
    service.report_malfunction(report)
    
    # FORWARDING THE NEWLY CREATED REPORT
    result = service.forward_report_malfunction(report)
    
    assert isinstance(result, ReportUpdateEvent)
    assert result.report.status == "managed"
    assert result.success == True
    
def test_resolve_report_malfunction(db_session):
    service = ReportAggregateService(ReportRepository(db_session), UserRepository(db_session), NotificationRepository(db_session), AdminRepository(db_session), ChargingStationRepository(db_session), CSOperatorRepository(db_session))
    
    report = Report(report_id=1, station_id=123, description="Report Description", severity="low", type="hardware", user_id=1)
    
    service.report_malfunction(report)
    
    # FORWARDING THE NEWLY CREATED REPORT
    service.forward_report_malfunction(report)
    
    # RESOLVING THE NEWLY CREATED REPORT
    result = service.resolve_report_malfunction(report)
    
    assert isinstance(result, ReportUpdateEvent)
    assert result.report.status == "resolved"
    assert result.success == True