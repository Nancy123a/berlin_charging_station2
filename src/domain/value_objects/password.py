from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Password:
    value: str

    def __post_init__(self):
        # Ensure the value is a string
        if not isinstance(self.value, str):
            raise TypeError(f"Password value must be a string, got {type(self.value).__name__}")
        
        # Perform validations and provide specific error messages
        if len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', self.value):
            raise ValueError("Password must contain at least one uppercase letter (A-Z).")

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', self.value):
            raise ValueError("Password must contain at least one lowercase letter (a-z).")

        # Check for at least one digit
        if not re.search(r'\d', self.value):
            raise ValueError("Password must contain at least one numeric digit (0-9).")

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', self.value):
            raise ValueError("Password must contain at least one special character (e.g., !@#$%^&*).")
        else:
            return True