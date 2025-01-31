from datetime import datetime
from src.search_context.domain.value_objects.postal_code import PostalCode

class PostalCodeFoundEvent:
    def __init__(self, postal_code: PostalCode):
        if not isinstance(postal_code, PostalCode):
            raise TypeError("postal_code must be an instance of PostalCode")
        
        self.postal_code = postal_code.value  # Store as string
        self.timestamp = datetime.utcnow()
        self.success = True  # Indicating failure

    def __repr__(self):
        return f"<PostalCodeFoundEvent(postal_code={self.postal_code}, success={self.success})>"

    def as_dict(self):
        return {
            "postal_code": self.postal_code,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
