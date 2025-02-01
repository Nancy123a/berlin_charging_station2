from datetime import datetime
from typing import List
from src.report_context.domain.entities.report import Report

class GetAdminReportsEvent:
    def __init__(self, reports: List[Report], admin_id: int, success: bool = True):
      self.reports = reports
      self.admin_id = admin_id
      self.success = success
      self.timestamp = datetime.now()

    def __repr__(self):
      return f"<GetAdminReportsEvent(reports={self.reports}, admin_id={self.admin_id}, success={self.success})>"

    def as_dict(self):
      return {
        "reports": self.reports,
        "admin_id": self.admin_id,
        "success": self.success,
        "timestamp": self.timestamp.isoformat()
      }