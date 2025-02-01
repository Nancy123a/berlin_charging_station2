from datetime import datetime
from typing import List
from src.register_context.domain.entities.admin import Admin

class GetAllAdminsEvent:
    def __init__(self, admins: List[Admin], success: bool = True):
      self.admins = admins
      self.success = success
      self.timestamp = datetime.now() 

    def __repr__(self):
      return f"<GetAdminsEvent(admins={self.admins}, success={self.success})>"

    def as_dict(self):
      return {
        "admins": self.admins,
        "success": self.success,
        "timestamp": self.timestamp.isoformat()
      }