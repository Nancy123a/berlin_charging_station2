# domain/services/user_service.py
from src.register_context.domain.entities.users import User
from src.register_context.domain.events.UserCreatedEvent import UserCreatedEvent
from src.register_context.domain.events.UserLoginEvent import UserLoginEvent
from src.register_context.domain.events.UserNotFoundEvent import UserNotFoundEvent
from src.register_context.infrastructure.repositories.UserRepository import UserRepository

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(self, username: str, password: str) -> UserCreatedEvent:
        # Check if the user already exists
        
        existing_user = self.user_repository.get_user_by_username(username)
        if existing_user:
            # User already exists, return failure event
            return UserNotFoundEvent(username, password, "User already exists")

        # Otherwise, create the user and return success event
        new_user = User(username=username, password=password)
        self.user_repository.add_user(new_user)

        return UserCreatedEvent(new_user.user_id, new_user.username, new_user.password)

    def login_user(self, username: str, password: str) -> UserLoginEvent:
        existing_user = self.user_repository.signin_user(username, password)
        if not existing_user:
            # User not found, return failure event
            return UserNotFoundEvent(username, password, "User not found")

        return UserLoginEvent(username=username, password=password)
