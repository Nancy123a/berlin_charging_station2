# domain/events/user/user_not_found_event.py
from datetime import datetime

class UserFoundEvent:
    def __init__(self, user_id:int, username: str,password:str, reason: str, success: bool = False):
        self.user_id = user_id
        self.username = username
        self.password=password
        self.reason = reason
        self.success = True
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<UserFoundEvent(username={self.username}, reason={self.reason}, success={self.success})>"

    def as_dict(self):
        return {
            "user_id":self.user_id,
            "username": self.username,
            "password":self.password,
            "reason": self.reason,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
