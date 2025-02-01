from datetime import datetime
from src.report_context.domain.entities.report import Report

class ReportAlreadyExistsEvent:
    def __init__(self, exisiting_report: Report, reason: str, success: bool = False):
        self.exisiting_report = exisiting_report
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<ReportAlreadyExistsEvent(exisiting_report={self.exisiting_report}, reason={self.reason}, success={self.success})>"

    def as_dict(self):
        return {
            "exisiting_report": self.exisiting_report,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }