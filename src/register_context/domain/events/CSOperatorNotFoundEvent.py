# domain/events/user/user_not_found_event.py
from datetime import datetime

class CSOperatorNotFoundEvent:
    def __init__(self, username: str,password:str, reason: str, success: bool = False):
        self.username = username
        self.password=password
        self.reason = reason
        self.success = success
        self.timestamp = datetime.utcnow()

    def __repr__(self):
        return f"<CSOperatorNotFoundEvent(username={self.username}, reason={self.reason}, success={self.success})>"

    def as_dict(self):
        return {
            "username": self.username,
            "password":self.password,
            "reason": self.reason,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
