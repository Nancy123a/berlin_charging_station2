from src.report_context.infrastructure.repositories.ReportRepository import ReportRepository
from src.report_context.domain.entities.report import Report
from src.report_context.domain.events.ReportUpdateEvent import ReportUpdateEvent
from src.report_context.domain.events.GetAllReportsEvent import GetAllReportsEvent
from src.report_context.domain.events.GetAdminReportsEvent import GetAdminReportsEvent
from src.report_context.domain.events.ReportCreateEvent import ReportCreateEvent
from src.report_context.domain.events.ReportAlreadyExistsEvent import ReportAlreadyExistsEvent

class ReportService:
  def __init__(self, report_repository: ReportRepository):
      """Initialize the service with a ReportRepository."""
      self.report_repository = report_repository
      
  def create_report(self, report: Report) -> ReportCreateEvent | ReportAlreadyExistsEvent:
      """Create a new report."""
      exisiting_reports = self.report_repository.find_reports_by_station_id(report.station_id)
      
      for exisiting_report in exisiting_reports:
          if exisiting_report is not None and exisiting_report.status != "resolved":
            return ReportAlreadyExistsEvent(exisiting_report, "Malfunction report has already been forwarded for this station")
        
      success = self.report_repository.create_report(report)
      return ReportCreateEvent(success)

  def get_reports_by_admin_id(self, admin_id: int) -> GetAdminReportsEvent:
      """Find reports by an admin ID."""
      reports = self.report_repository.find_reports_by_admin_id(admin_id)
      return GetAdminReportsEvent(reports, admin_id)
  
  def get_reports_by_csoperator_id(self, csoperator_id: int) -> GetAllReportsEvent:
      """Find reports by a CS operator ID."""
      reports = self.report_repository.find_reports_by_csoperator_id(csoperator_id)
      return GetAllReportsEvent(reports)
  
  def update_report(self, report: Report) -> ReportUpdateEvent:
      """Update a report in the database."""
      updated_event = self.report_repository.update_report(report)
      return ReportUpdateEvent(updated_event)