# repository/user_repository.py
from src.register_context.domain.entities.csoperator import CSOperator
from src.register_context.domain.value_objects import Password
from sqlalchemy.orm import Session

class CSOperatorRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_csoperator_by_username(self, username: str) -> CSOperator:
        return self.session.query(CSOperator).filter(CSOperator.username == username).first()

    def add_csoperator(self, csoperator: CSOperator):
        self.session.add(csoperator)
        self.session.commit()

    def signin_csoperator(self, username: str, password: str) -> bool:
        return self.session.query(CSOperator).filter_by(username=username,password=password).first()
    
    def get_all_csoperators(self):
        return self.session.query(CSOperator).all()
    
    def update_csoperator(self, csoperator: CSOperator):
        self.session.merge(csoperator)
        self.session.commit()