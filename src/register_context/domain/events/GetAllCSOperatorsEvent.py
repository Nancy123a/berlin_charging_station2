from datetime import datetime
from typing import List
from src.register_context.domain.entities.csoperator import CSOperator

class GetAllCSOperatorsEvent:
    def __init__(self, csoperators: List[CSOperator], success: bool = True):
      self.csoperators = csoperators
      self.success = success
      self.timestamp = datetime.now()

    def __repr__(self):
      return f"<GetAllCSOperatorsEvent(csoperators={self.csoperators}, success={self.success})>"

    def as_dict(self):
      return {
        "csoperators": self.csoperators,
        "success": self.success,
        "timestamp": self.timestamp.isoformat()
      }