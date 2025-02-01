import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from database.database import Base
from sqlalchemy.orm import sessionmaker
from src.register_context.domain.entities.admin import Admin
from src.report_context.domain.entities.notification import Notification
from src.register_context.domain.entities.users import User
from src.register_context.domain.entities.csoperator import CSOperator
from src.search_context.domain.entities.chargingstation import ChargingStation
from src.report_context.domain.entities.report import Report
from src.report_context.application.services.ReportService import ReportService
from src.report_context.infrastructure.repositories.ReportRepository import ReportRepository
from src.report_context.domain.events.ReportAlreadyExistsEvent import ReportAlreadyExistsEvent
from src.report_context.domain.events.ReportCreateEvent import ReportCreateEvent
from sqlalchemy.exc import IntegrityError
      
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
    

def test_valid_report_instance(db_session):
    report = Report(description = "Report Description", severity = "low", type = "hardware", station_id = 123, user_id = 1, admin_id = 1)
    assert report.description == "Report Description"
    assert report.severity == "low"
    assert report.type == "hardware"
    assert report.station_id == 123
    assert report.user_id == 1
    assert report.admin_id == 1
    
def test_invalid_report_instance(db_session):
    report = Report(description = None, severity = "low", type = "hardware", station_id = 123, user_id = 1, admin_id = 1)
    assert report.description == None
    assert report.severity == "low"
    assert report.type == "hardware"
    assert report.station_id == 123
    assert report.user_id == 1
    assert report.admin_id == 1
    
def test_report_creation(db_session):
    service = ReportService(ReportRepository(db_session))
    report = Report(description = "Report Description", severity = "low", type = "hardware", station_id = 123, user_id = 1, admin_id = 1)
    result = service.create_report(report)
    assert isinstance(result, ReportCreateEvent)
    assert result.success == True
    
def test_duplicate_report_creation(db_session):
    service = ReportService(ReportRepository(db_session))
    report_1 = Report(description = "Report Description", severity = "low", type = "hardware", station_id = 123, user_id = 1, admin_id = 1)
    result = service.create_report(report_1)
    assert isinstance(result, ReportCreateEvent)
    assert result.success == True
    result_duplicate = service.create_report(report_1)
    assert isinstance(result_duplicate, ReportAlreadyExistsEvent)
    assert result_duplicate.success == False

def test_invalid_report_creation(db_session):
    service = ReportService(ReportRepository(db_session))
    report = Report(description = None, severity = "low", type = "hardware", station_id = 123, user_id = 1, admin_id = 1)
    try:
        service.create_report(report)
        assert False, "Expected IntegrityError"
    except IntegrityError as e:
        pass
     
def test_get_reports_by_admin_id(db_session):
    service = ReportService(ReportRepository(db_session))
    
    test_report_creation(db_session)
    
    reports_result = service.get_reports_by_admin_id(1)
    
    assert len(reports_result.reports) == 1
    assert reports_result.success == True
    
def test_get_reports_by_admin_id_not_found(db_session):
    service = ReportService(ReportRepository(db_session))
    
    reports_result = service.get_reports_by_admin_id(2)
    
    assert len(reports_result.reports) == 0
    assert reports_result.success == True
    
def test_forward_report_by_admin_id(db_session):
    service = ReportService(ReportRepository(db_session))
    
    test_report_creation(db_session)
    
    reports_result = service.get_reports_by_admin_id(1)  
      
    report = reports_result.reports[0]
    report.csoperator_id = 1
    report.status = "managed"
    
    updated_report = service.update_report(report)
        
    assert updated_report.report.report_id == report.report_id
    assert updated_report.success == True

def test_get_reports_by_csoperator_id(db_session):
    service = ReportService(ReportRepository(db_session))
    
    test_forward_report_by_admin_id(db_session)
    
    reports_result = service.get_reports_by_csoperator_id(1)
    
    assert len(reports_result.reports) == 1
    assert reports_result.success == True
    
def test_resolve_report_by_csoperator_id(db_session):
    service = ReportService(ReportRepository(db_session))
    
    test_forward_report_by_admin_id(db_session)
    
    reports_result = service.get_reports_by_csoperator_id(1)
    
    report = reports_result.reports[0]
    report.status = "resolved"
    
    updated_report = service.update_report(report)
        
    assert updated_report.report.report_id == report.report_id
    assert updated_report.success == True