from datetime import datetime

class UpdateCSOperatorEvent:
    def __init__(self, csoperator_id: int, username: str, password: str, success: bool = True):
        self.csoperator_id = csoperator_id
        self.username = username
        self.password = password
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<UpdateCSOperatorEvent(csoperator_id={self.csoperator_id}, username={self.username}, password={self.password}, success={self.success})>"

    def as_dict(self):
        return {
            "csoperator_id": self.csoperator_id,
            "username": self.username,
            "password": self.password,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        } 