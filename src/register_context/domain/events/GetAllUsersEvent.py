from datetime import datetime
from typing import List
from src.register_context.domain.entities.users import User

class GetAllUsersEvent:
    def __init__(self, users: List[User], success: bool = True):
      self.users = users
      self.success = success
      self.timestamp = datetime.now()

    def __repr__(self):
      return f"<GetAllUsersEvent(users={self.users}, success={self.success})>"

    def as_dict(self):
      return {
        "users": self.users,
        "success": self.success,
        "timestamp": self.timestamp.isoformat()
      } 