from datetime import datetime
from src.report_context.domain.entities.report import Report

class ReportCreateEvent:
    def __init__(self, report: Report, success: bool = True):
        self.report = report
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<ReportCreateEvent(report={self.report}, success={self.success})>"

    def as_dict(self):
        return {
            "report": self.report,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }