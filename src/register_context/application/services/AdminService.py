# domain/services/user_service.py
from src.register_context.domain.entities.admin import Admin
from src.register_context.domain.events.AdminCreatedEvent import AdminCreatedEvent
from src.register_context.domain.events.AdminLoginEvent import AdminLoginEvent
from src.register_context.domain.events.AdminNotFoundEvent import AdminNotFoundEvent
from src.register_context.infrastructure.repositories.AdminRepository import AdminRepository

class AdminService:
    def __init__(self, admin_repository: AdminRepository):
        self.admin_repository = admin_repository

    def register_admin(self, username: str, password: str) -> AdminCreatedEvent:
        # Check if the user already exists
        existing_admin = self.admin_repository.get_admin_by_username(username)
        if existing_admin:
            # User already exists, no need to create, return failure event
            return AdminNotFoundEvent(username,password, "Admin already exists")

        # Otherwise, create the user and return success event
        new_admin = Admin(username=username, password=password,number_reports_assigned=0)
        self.admin_repository.add_admin(new_admin)

        return AdminCreatedEvent(new_admin.sys_admin_id, new_admin.username,new_admin.password)

    def login_admin(self,username:str,password:str) -> AdminLoginEvent:
        existing_admin=self.admin_repository.signin_admin(password,username)
        if existing_admin:
            # User already exists, no need to create, return failure event
            return AdminNotFoundEvent(username,password, "Admin already exists")

        return AdminLoginEvent(username,password)