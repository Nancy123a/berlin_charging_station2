from dataclasses import dataclass
import re

@dataclass(frozen=True)
class PostalCode:
    value: str

    def __post_init__(self):
        # Ensure the value is a string
        if not isinstance(self.value, str):
            raise TypeError(f"PostalCode value must be a string, got {type(self.value).__name__}")
        
        # Validate the postal code value
        if not self.value.isdigit():
            raise ValueError(f"PostalCode must contain only numeric characters, got: {self.value}")
        
        if not self.is_valid():
            raise ValueError(f"Invalid postal code: {self.value}")

    def is_valid(self) -> bool:
        # Regex pattern for valid postal codes: starts with 10, 12, 13, or 14 and has 3 additional digits
        pattern = r'^(10|12|13|14)\d{3}$'
        return bool(re.match(pattern, self.value))
