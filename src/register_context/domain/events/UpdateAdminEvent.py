from datetime import datetime
from src.register_context.domain.value_objects.password import Password

class UpdateAdminEvent:
    def __init__(self, admin_id: int, username: str, password: Password, success: bool = True):
        self.admin_id = admin_id
        self.username = username
        self.password = password
        self.success = success
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<UpdateAdminEvent(admin_id={self.admin_id}, username={self.username}, password={self.password}, success={self.success})>"

    def as_dict(self):
        return {
            "admin_id": self.admin_id,
            "username": self.username,
            "password": self.password,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }