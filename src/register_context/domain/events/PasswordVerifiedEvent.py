# domain/events/user/user_not_found_event.py
from datetime import datetime

class PasswordVerifiedEvent:
    def __init__(password:str, success: bool = False):
        self.password=password
        self.success = True
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<PasswordVerifiedEvent(success={self.success})>"

    def as_dict(self):
        return {
            "password":self.password,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }