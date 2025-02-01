from dataclasses import dataclass

@dataclass(frozen=True)
class ReportType:
    value: str

    def __post_init__(self):
        # Ensure the value is a string
        if not isinstance(self.value, str):
            raise TypeError(f"Type value must be a string, got {type(self.value).__name__}")
        
        # Validate the type value
        if not self.value:
            raise ValueError(f"Type must not be empty.")  # Ensure we don't make redundant changes
          
        # Ensure the type is "hardware", "software" or "connectivity"   
        if self.value not in ["hardware", "software", "connectivity"]:
            raise ValueError(f"Type must be one of 'hardware' or 'software'.")
          
        return self.value