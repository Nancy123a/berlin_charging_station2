import pytest
import sys
from pathlib import Path
import os

project_root = Path(os.getcwd()).resolve().parent.parent  # Adjust .parent if needed
sys.path.append(str(project_root))

from core.register_methods import inspect_and_create_tables, register_login

import pytest
from unittest.mock import MagicMock, patch
from src.register_context.domain.events.UserLoginEvent import UserLoginEvent
from src.register_context.domain.events.UserCreatedEvent import UserCreatedEvent
from src.register_context.domain.events.PasswordVerifiedEvent import PasswordVerifiedEvent


# Mock Streamlit components
@pytest.fixture
def mock_st(mocker):
    mocker.patch('streamlit.sidebar.selectbox', return_value='Login')
    mocker.patch('streamlit.text_input', side_effect=['test_user', 'Abc123...', 'Abc123...'])
    mocker.patch('streamlit.selectbox', return_value='user')
    mocker.patch('streamlit.button', return_value=True)
    mocker.patch('streamlit.error')
    mocker.patch('streamlit.success')
    mocker.patch('streamlit.subheader')

def test_inspect_and_create_tables(mocker):
    mock_inspect = mocker.patch('core.register_methods.inspect')
    mock_engine = mocker.patch('core.register_methods.engine')
    mock_base = mocker.patch('core.register_methods.Base')

    mock_inspector = mock_inspect.return_value
    mock_inspector.get_table_names.return_value = []

    inspect_and_create_tables()

    assert mock_base.metadata.create_all.called

def test_register_login_login_success(mock_st, mocker):
    mock_service = MagicMock()
    mock_service.verify_password.return_value = PasswordVerifiedEvent("Abc123...")
    mock_service.login_user.return_value = UserLoginEvent(user_id=1, username="test_user", password="Abc123...")

    mock_repo = MagicMock(return_value=mock_service)
    
    with patch('core.register_methods.UserRepository', mock_repo):
        with patch('core.register_methods.UserService', return_value=mock_service):
            role, user_id = register_login()

    assert role == 'user'
    assert user_id == 1

def test_register_login_register_success(mock_st, mocker):
    mock_st = mocker.patch('streamlit.sidebar.selectbox', return_value='Register')
    mock_service = MagicMock()
    mock_service.verify_password.return_value = PasswordVerifiedEvent("Abc123...")
    mock_service.register_user.return_value = UserCreatedEvent(user_id=1, username="test_user", password="Abc123...")

    mock_repo = MagicMock(return_value=mock_service)
    
    with patch('core.register_methods.UserRepository', mock_repo):
        with patch('core.register_methods.UserService', return_value=mock_service):
            role, _ = register_login()

    assert role == 'user'
    
    