from sqlalchemy.orm import Session
from database.database import SessionLocal  # Ensure SessionLocal is imported

from src.report_context.domain.entities.report import Report

class ReportRepository: 
  def __init__(self, session: Session = None):
        """Initialize the repository with a SQLAlchemy session."""
        self.session = session or SessionLocal()
  
  def create_report(self, report: Report):
      """Create a new report in the database."""
      self.session.add(report)
      self.session.commit()

  def find_report_by_id(self, report_id: int):
      """Find a report by its ID."""
      report = self.session.query(Report).filter_by(report_id=report_id).first()
      return report

  def find_reports_by_station_id(self, station_id: int):
      """Find reports by a station ID."""
      reports = self.session.query(Report).filter_by(station_id=station_id).all()
      return reports

  def find_reports_by_user_id(self, user_id: int):
      """Find reports by a user ID."""
      reports = self.session.query(Report).filter_by(user_id=user_id).all()
      return reports

  def find_reports_by_admin_id(self, admin_id: int):
      """Find reports by an admin ID."""
      reports = self.session.query(Report).filter_by(admin_id=admin_id).all()
      return reports

  def find_reports_by_csoperator_id(self, csoperator_id: int):
      """Find reports by a CS operator ID."""
      reports = self.session.query(Report).filter_by(csoperator_id=csoperator_id).all()
      return reports

  def find_reports_by_status(self, status: str):
      """Find reports by a status."""
      reports = self.session.query(Report).filter_by(status=status).all()
      return reports

  def find_reports_by_description(self, description: str):
      """Find reports by a description."""
      reports = self.session.query(Report).filter_by(description=description).all()
      return reports

  def find_reports_by_severity(self, severity: str):
      """Find reports by a severity."""
      reports = self.session.query(Report).filter_by(severity=severity).all()
      return reports

  def find_reports_by_created_at(self, created_at: str):
      """Find reports by a created_at."""
      reports = self.session.query(Report).filter_by(created_at=created_at).all()
      return reports

  def find_reports_by_updated_at(self, updated_at: str):
      """Find reports by an updated_at."""
      reports = self.session.query(Report).filter_by(updated_at=updated_at).all()
      return reports

  def find_reports_by_all(self, station_id: int, user_id: int, admin_id: int, csoperator_id: int, status: str, description: str, severity: str, created_at: str, updated_at: str):
      """Find reports by multiple parameters."""
      reports = self.session.query(Report).filter_by(station_id=station_id, user_id=user_id, admin_id=admin_id, csoperator_id=csoperator_id, status=status, description=description, severity=severity, created_at=created_at, updated_at=updated_at).all()
      return reports

  def update_report(self, report: Report):
      """Update a report in the database."""
      self.session.merge(report)
      self.session.commit()

  def delete_report(self, report_id: int):
      """Delete a report from the database."""
      report = self.session.query(Report).filter_by(report_id=report_id).first()
      self.session.delete(report)
      self.session.commit()     