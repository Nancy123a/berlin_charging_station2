from typing import List
from src.domain.value_objects.password import Password
from src.repositories.register_repository import RegisterRepository

class RegisterService:
    def __init__(self, repository: RegisterRepository):
        self.repository = repository

    def register_user_admin_csoperator(self, password: Password,username:str,type:str) -> bool:
        """Register user, admin, cs operator"""
        if type == "user":
            return self.repository.register_user(password, username)
            
        elif type == "admin":
            return self.repository.register_admin(password, username)
            
        else:
            return self.repository.register_csoperator(password, username)

    def login(self,password:Password,username:str,type:str) -> bool:
        if type == "user":
            return self.repository.login_user(password, username)
            
        elif type == "admin":
            return self.repository.login_admin(password, username)
            
        else:
            return self.repository.login_csoperator(password, username)