# domain/events/user/user_not_found_event.py
from datetime import datetime

class PasswordNotVerifiedEvent:
    def __init__(self, username: str,password:str, reason: str, success: bool = False):
        self.password=password
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<PasswordNotVerifiedEvent(success={self.success})>"

    def as_dict(self):
        return {
            "password":self.password,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
