# repository/user_repository.py
from src.register_context.domain.entities.admin import Admin
from src.register_context.domain.value_objects import Password
from src.register_context.domain.events.AdminAlreadyExistEvent import AdminAlreadyExistEvent
from sqlalchemy.orm import Session
from typing import List

class AdminRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_admin_by_username(self, username: str) -> Admin:
        admin=self.session.query(Admin).filter(Admin.username == username).first()
        if admin:
            return AdminAlreadyExistEvent(admin.username,admin.password,"Admin already exist")
        return admin

    def add_admin(self, admin: Admin):
        self.session.add(admin)
        self.session.commit()

    def signin_admin(self, username: str, password: Password) -> bool:
        return self.session.query(Admin).filter_by(username=username,password=password).first()
    
    def get_all_admins(self) -> List[Admin]:
        return self.session.query(Admin).all()
    
    def update_admin(self, admin: Admin) -> Admin:
        updated_admin = self.session.merge(admin)
        self.session.commit()
        return updated_admin
 