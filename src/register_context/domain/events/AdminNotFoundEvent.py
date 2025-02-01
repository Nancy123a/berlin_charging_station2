# domain/events/user/user_not_found_event.py
from datetime import datetime

class AdminNotFoundEvent:
    def __init__(self, username: str,password:str, reason: str, success: bool = False):
        self.username = username
        self.password=password
        self.reason = reason
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<UserNotFoundEvent(username={self.username}, reason={self.reason}, success={self.success})>"

    def as_dict(self):
        return {
            "username": self.username,
            "password":self.password,
            "reason": self.reason,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
