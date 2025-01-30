# domain/events/user/user_created_event.py
from datetime import datetime

class CSOperatorCreatedEvent:
    def __init__(self, user_id: int, username: str,password:str, success: bool = True):
        self.cs_operator_id = user_id
        self.username = username
        self.password = password
        self.success = success
        self.timestamp = datetime.utcnow()

    def __repr__(self):
        return f"<CSOperatorCreatedEvent(user_id={self.user_id}, username={self.username}, password={self.password} success={self.success})>"

    def as_dict(self):
        return {
            "user_id": self.cs_operator_id,
            "username": self.username,
            "password":self.password,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
