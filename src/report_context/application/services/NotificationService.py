from src.report_context.infrastructure.repositories.NotificationRepository import NotificationRepository
from typing import List
from src.report_context.domain.events.NotificationCreateEvent import NotificationCreateEvent
from src.report_context.domain.events.GetUserNotificationsEvent import GetUserNotificationsEvent

class NotificationService:
  def __init__(self, notification_repository: NotificationRepository):
      """Initialize the service with a NotificationRepository."""
      self.notification_repository = notification_repository
  
  def create_notifications(self, users_id: List[int], content: str) -> NotificationCreateEvent:
      """Create a new notification."""
      success = self.notification_repository.create_notifications(users_id, content)
      return NotificationCreateEvent(success)
  
  def get_notifications_by_user_id(self, user_id: int) -> GetUserNotificationsEvent:
      """Find notifications by a user ID."""
      notifications = self.notification_repository.find_notifications_by_user_id(user_id)
      return GetUserNotificationsEvent(notifications, user_id)