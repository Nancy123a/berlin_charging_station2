from src.report_context.infrastructure.repositories.ReportRepository import ReportRepository
from src.report_context.domain.entities.report import Report
from src.register_context.domain.entities.admin import Admin
from typing import List

class ReportService:
  def __init__(self, report_repository: ReportRepository):
      """Initialize the service with a ReportRepository."""
      self.report_repository = report_repository
      
  def create_report(self, report: Report):
      """Create a new report."""
      exisiting_reports = self.report_repository.find_reports_by_station_id(report.station_id)
      
      for exisiting_report in exisiting_reports:
          if exisiting_report is not None and exisiting_report.status != "resolved":
            # Report already exists and is not resolved, return failure event
            raise ValueError("Malfunction report has already been forwarded for this station")
      
      self.report_repository.create_report(report)

  def get_reports_by_admin_id(self, admin_id: int):
      """Find reports by an admin ID."""
      reports = self.report_repository.find_reports_by_admin_id(admin_id)
      return reports
  
  def get_reports_by_csoperator_id(self, csoperator_id: int):
      """Find reports by a CS operator ID."""
      reports = self.report_repository.find_reports_by_csoperator_id(csoperator_id)
      return reports
  
  def update_report(self, report: Report):
      """Update a report in the database."""
      self.report_repository.update_report(report)
    