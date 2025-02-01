from datetime import datetime
from typing import List
from src.report_context.domain.entities.notification import Notification

class GetUserNotificationsEvent:
  def __init__(self, notifications: List[Notification], user_id: int, success: bool = True):
      self.user_id = user_id
      self.notifications = notifications
      self.success = success
      self.timestamp = datetime.now()

  def __repr__(self):
    return f"<GetUserNotificationsEvent(notifications={self.notifications}, user_id={self.user_id}, success={self.success})>"

  def as_dict(self):
    return {
      "notifications": self.notifications,
      "user_id": self.user_id,
      "success": self.success,
      "timestamp": self.timestamp.isoformat()
    }