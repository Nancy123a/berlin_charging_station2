from datetime import datetime

class ReportDeleteEvent:
    def __init__(self, report_id: int, success: bool = True):
        self.report_id = report_id
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<ReportDeleteEvent(report_id={self.report_id}, success={self.success})>"

    def as_dict(self):
        return {
            "report_id": self.report_id,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }