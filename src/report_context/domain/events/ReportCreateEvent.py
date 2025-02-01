from datetime import datetime
from src.report_context.domain.entities.report import Report

class ReportCreateEvent:
    def __init__(self, success: bool = True):
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<ReportCreateEvent(success={self.success})>"

    def as_dict(self):
        return {
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }