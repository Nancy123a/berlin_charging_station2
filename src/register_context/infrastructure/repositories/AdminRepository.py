# repository/user_repository.py
from src.register_context.domain.entities.admin import Admin
from src.register_context.domain.value_objects import Password
from sqlalchemy.orm import Session

class AdminRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_admin_by_username(self, username: str) -> Admin:
        return self.session.query(Admin).filter(Admin.username == username).first()

    def add_admin(self, admin: Admin):
        self.session.add(admin)
        self.session.commit()

    def signin_admin(self, username: str, password: Password) -> bool:
        return self.session.query(Admin).filter_by(username=username,password=password).first()
 