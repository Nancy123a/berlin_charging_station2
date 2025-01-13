import sys
import os

domain_directory = os.path.abspath(os.path.join(os.getcwd(), '..', 'domain'))

# Add both directories to sys.path
sys.path.append(domain_directory) 

from abc import ABC, abstractmethod
from typing import List
from src.domain.value_objects.password import Password

class IRegisterRepository(ABC):
    @abstractmethod
    def register_user(self, password: Password, username: str) -> bool:
        """Register a user with a given password and username."""
        pass
    
    @abstractmethod
    def register_admin(self, password: Password, username: str) -> bool:
        """Register an admin with a given password and username."""
        pass
    
    @abstractmethod
    def register_csoperator(self, password: Password, username: str) -> bool:
        """Register a charging station operator with a given password and username."""
        pass

    @abstractmethod
    def login_user(self, password: Password, username: str) -> bool:
        """login a user with a given password and username."""
        pass
    
    @abstractmethod
    def login_admin(self, password: Password, username: str) -> bool:
        """login an admin with a given password and username."""
        pass
    
    @abstractmethod
    def login_csoperator(self, password: Password, username: str) -> bool:
        """login a charging station operator with a given password and username."""
        pass