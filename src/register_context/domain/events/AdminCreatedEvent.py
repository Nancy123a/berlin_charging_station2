# domain/events/user/user_created_event.py
from datetime import datetime

class AdminCreatedEvent:
    def __init__(self, sys_admin_id: int, username: str,password:str, success: bool = True):
        self.sys_admin_id = sys_admin_id
        self.username = username
        self.password = password
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<AdminCreatedEvent(user_id={self.user_id}, username={self.username}, password={self.password} success={self.success})>"

    def as_dict(self):
        return {
            "user_id": self.sys_admin_id,
            "username": self.username,
            "password":self.password,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
