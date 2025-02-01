# repository/user_repository.py
from src.register_context.domain.entities.users import User
from src.register_context.domain.value_objects import Password
from src.register_context.domain.events.UserAlreadyExistEvent import UserAlreadyExistEvent

from sqlalchemy.orm import Session
from typing import List

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_username(self, username: str) -> UserAlreadyExistEvent | User:
        user=self.session.query(User).filter(User.username == username).first()
        if user:
            return UserAlreadyExistEvent(user.username,user.password,"User already exist")
        return user

    def add_user(self, user: User):
        self.session.add(user)
        self.session.commit()

    def signin_user(self, username: str, password: str) -> bool:
        return self.session.query(User).filter_by(username=username,password=password).first()
    
    def get_all_users(self) -> List[User]:
        return self.session.query(User).all()
