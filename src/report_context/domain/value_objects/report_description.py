from dataclasses import dataclass

@dataclass(frozen=True)
class ReportDescription:
    value: str

    def __post_init__(self):
        # Ensure the value is a string
        if not isinstance(self.value, str):
            raise TypeError(f"Description value must be a string, got {type(self.value).__name__}")
        
        # Validate the description value
        if not self.value:
            raise ValueError(f"Description must not be empty.")  # Ensure we don't make redundant changes
          
        # Ensure the description is not too short
        if len(self.value) < 10:
            raise ValueError(f"Description must be at least 10 characters long.")
          
        return self.value

    