# domain/services/user_service.py
from src.register_context.domain.entities.admin import Admin
from src.register_context.domain.events.AdminCreatedEvent import AdminCreatedEvent
from src.register_context.domain.events.AdminLoginEvent import AdminLoginEvent
from src.register_context.domain.events.AdminNotFoundEvent import AdminNotFoundEvent
from src.register_context.infrastructure.repositories.AdminRepository import AdminRepository
from src.register_context.domain.value_objects.password import Password
from src.register_context.domain.events.GetAllAdminsEvent import GetAllAdminsEvent
from src.register_context.domain.events.UpdateAdminEvent import UpdateAdminEvent

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

    def login_admin(self, username: str, password: str) -> AdminLoginEvent | AdminNotFoundEvent:
        existing_admin = self.admin_repository.signin_admin(username, password)
        if not existing_admin:
            # User not found, return failure event
            return AdminNotFoundEvent(username, password, "CSOperator not found")

        return AdminLoginEvent(existing_admin.sys_admin_id,username, password)

    def verify_password(self,password:str):
        return Password(password)
    
    def get_all_admins(self) -> GetAllAdminsEvent:
        all_admins = self.admin_repository.get_all_admins()
        return GetAllAdminsEvent(all_admins)
    
    def update_admin(self, admin: Admin) -> UpdateAdminEvent:
        updated_admin = self.admin_repository.update_admin(admin)
        return UpdateAdminEvent(updated_admin.sys_admin_id, updated_admin.username, updated_admin.password)