from dataclasses import dataclass

@dataclass(frozen=True)
class ReportSeverity:
    value: str

    def __post_init__(self):
        # Ensure the value is a string
        if not isinstance(self.value, str):
            raise TypeError(f"Severity value must be a string, got {type(self.value).__name__}")
        
        # Validate the severity value
        if not self.value:
            raise ValueError(f"Severity must not be empty.")  # Ensure we don't make redundant changes
          
        # Ensure the severity is "low", "medium", or "high"
        if self.value not in ["low", "medium", "high"]:
            raise ValueError(f"Severity must be one of 'low', 'medium', or 'high'.")
          
        return self.value