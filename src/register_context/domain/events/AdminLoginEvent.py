# domain/events/user/user_created_event.py
from datetime import datetime

class AdminLoginEvent:
    def __init__(self, username: str, password:str, success: bool = True):
        self.username = username
        self.password=password
        self.success = success
        self.timestamp = datetime.utcnow()

    def __repr__(self):
        return f"<AdminLoginEvent(user_id={self.user_id}, username={self.username}, password={self.password}, success={self.success})>"

    def as_dict(self):
        return {
            "username": self.username,
            "password":self.password,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
