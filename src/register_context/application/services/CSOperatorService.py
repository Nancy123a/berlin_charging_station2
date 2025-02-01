# domain/services/user_service.py
from src.register_context.domain.entities.csoperator import CSOperator
from src.register_context.domain.events.CSOperatorCreatedEvent import CSOperatorCreatedEvent
from src.register_context.domain.events.CSOperatorLoginEvent import CSOperatorLoginEvent
from src.register_context.domain.events.CSOperatorNotFoundEvent import CSOperatorNotFoundEvent
from src.register_context.infrastructure.repositories.CSOperatorRepository import CSOperatorRepository
from src.register_context.domain.value_objects.password import Password
from src.register_context.domain.events.GetAllCSOperatorsEvent import GetAllCSOperatorsEvent
from src.register_context.domain.events.UpdateCSOperatorEvent import UpdateCSOperatorEvent

class CSOperatorService:
    def __init__(self, csoperator_repository: CSOperatorRepository):
        self.csoperator_repository = csoperator_repository

    def register_csoperator(self, username: str, password: str) -> CSOperatorCreatedEvent:
        # Check if the user already exists
        existing_csoperator = self.csoperator_repository.get_csoperator_by_username(username)
        if existing_csoperator:
            # User already exists, return failure event
            return CSOperatorNotFoundEvent(username, password, "CSOperator already exists")

        # Otherwise, create the user and return success event
        new_csoperator = CSOperator(username=username, password=password, number_reports_assigned=0)
        self.csoperator_repository.add_csoperator(new_csoperator)

        return CSOperatorCreatedEvent(new_csoperator.cs_operator_id, new_csoperator.username, new_csoperator.password)

    def login_csoperator(self, username: str, password: str) -> CSOperatorLoginEvent:
        existing_csoperator = self.csoperator_repository.signin_csoperator(username, password)
        if not existing_csoperator:
            # User not found, return failure event
            return CSOperatorNotFoundEvent(username, password, "CSOperator not found")

        return CSOperatorLoginEvent(existing_csoperator.cs_operator_id,username, password)

    def verify_password(self,password:str):
        return Password(password)
    
    def get_all_csoperators(self) -> GetAllCSOperatorsEvent:
        all_csoperators = self.csoperator_repository.get_all_csoperators()
        return GetAllCSOperatorsEvent(all_csoperators)
    
    def update_csoperator(self, csoperator: CSOperator) -> UpdateCSOperatorEvent:
        updated_csoperator = self.csoperator_repository.update_csoperator(csoperator)
        return UpdateCSOperatorEvent(updated_csoperator.cs_operator_id, updated_csoperator.username, updated_csoperator.password)