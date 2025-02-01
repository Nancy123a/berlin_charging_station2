from datetime import datetime
from src.report_context.domain.entities.report import Report

class ReportCreateFailedEvent:
    def __init__(self, reason: str, success: bool = False):
        self.reason = reason
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<ReportCreateFailedEvent(reason={self.reason}, success={self.success})>"

    def as_dict(self):
        return {
            "reason": self.reason,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }