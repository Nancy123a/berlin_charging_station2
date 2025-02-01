from sqlalchemy.orm import Session
from database.database import SessionLocal  # Ensure SessionLocal is imported
from typing import List
from src.report_context.domain.entities.notification import Notification


class NotificationRepository: 
  def __init__(self, session: Session = None):
        """Initialize the repository with a SQLAlchemy session."""
        self.session = session or SessionLocal()
        
  def create_notifications(self, users_id: List[int], content: str) -> bool:
      """Create a new notification in the database."""
      self.session.bulk_save_objects([Notification(user_id=user_id, content=content) for user_id in users_id])
      self.session.commit()
      return True
      
  def find_notifications_by_user_id(self, user_id: int) -> List[Notification]:
      """Find notifications by a user ID."""
      notifications = self.session.query(Notification).filter_by(user_id=user_id).all()
      return notifications