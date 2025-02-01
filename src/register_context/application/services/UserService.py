# domain/services/user_service.py
from src.register_context.domain.entities.users import User
from src.register_context.domain.events.UserAlreadyExistEvent import UserAlreadyExistEvent
from src.register_context.domain.events.UserLoginEvent import UserLoginEvent
from src.register_context.domain.events.UserCreatedEvent import UserCreatedEvent
from src.register_context.infrastructure.repositories.UserRepository import UserRepository
from src.register_context.domain.value_objects.password import Password
from src.register_context.domain.events.GetAllUsersEvent import GetAllUsersEvent
from src.register_context.domain.events.PasswordVerifiedEvent import PasswordVerifiedEvent
from src.register_context.domain.events.PasswordNotVerifiedEvent import PasswordNotVerifiedEvent


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def verify_password(self,password:str):
        try:
            # Convert postal_code string to PostalCode object
            new_password = Password(password)
            return PasswordVerifiedEvent(new_password)
        except ValueError as e:
            return PasswordNotVerifiedEvent(Password(password),str(e))

    def register_user(self, username: str, password: str) -> UserCreatedEvent:
        # Check if the user already exists
        
        existing_user = self.user_repository.get_user_by_username(username)
        if isinstance(existing_user,UserAlreadyExistEvent):
            # User already exists, return failure event
            return  UserAlreadyExistEvent(username, password, "user already exists")
        
        # Otherwise, create the user and return success event
        new_user = User(username=username, password=password)
        self.user_repository.add_user(new_user)

        return UserCreatedEvent(new_user.user_id, new_user.username, new_user.password)

    def login_user(self, username: str, password: str) -> UserLoginEvent:
        existing_user = self.user_repository.signin_user(username, password)
        if not existing_user:
            # User not found, return failure event
            return UserAlreadyExistEvent(username, password, "User already exist")

        return UserLoginEvent(existing_user.user_id,username=username, password=password)
    
    def get_all_users(self) -> GetAllUsersEvent:
        all_users = self.user_repository.get_all_users()
        return GetAllUsersEvent(all_users)