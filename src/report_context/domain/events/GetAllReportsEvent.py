from datetime import datetime
from typing import List
from src.report_context.domain.entities.report import Report

class GetAllReportsEvent:
    def __init__(self, reports: List[Report], success: bool = True):
      self.reports = reports
      self.success = success
      self.timestamp = datetime.now()

    def __repr__(self):
      return f"<GetAllReportsEvent(reports={self.reports}, success={self.success})>"

    def as_dict(self):
      return {
        "reports": self.reports,
        "success": self.success,
        "timestamp": self.timestamp.isoformat()
      }