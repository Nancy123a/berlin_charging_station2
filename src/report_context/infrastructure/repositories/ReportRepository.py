from sqlalchemy.orm import Session
from database.database import SessionLocal  # Ensure SessionLocal is imported

from src.report_context.domain.entities.report import Report
from typing import List

class ReportRepository: 
  def __init__(self, session: Session = None):
        """Initialize the repository with a SQLAlchemy session."""
        self.session = session or SessionLocal()
  
  def create_report(self, report: Report) -> bool:
      """Create a new report in the database."""
      self.session.add(report)
      self.session.commit()
      return True
      
  def find_reports_by_station_id(self, station_id: int) -> List[Report]:
      """Find reports by a station ID."""
      reports = self.session.query(Report).filter_by(station_id=station_id).all()
      return reports

  def find_reports_by_admin_id(self, admin_id: int) -> List[Report]:
      """Find reports by an admin ID."""
      reports = self.session.query(Report).filter_by(admin_id=admin_id).all()
      return reports

  def find_reports_by_csoperator_id(self, csoperator_id: int) -> List[Report]:
      """Find reports by a CS operator ID."""
      reports = self.session.query(Report).filter_by(csoperator_id=csoperator_id).all()
      return reports

  def update_report(self, report: Report) -> Report:
      """Update a report in the database."""
      updated_report = self.session.merge(report)
      self.session.commit()
      return updated_report