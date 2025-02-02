import pytest
import sys
from pathlib import Path
import os

project_root = Path(os.getcwd()).resolve().parent.parent  # Adjust .parent if needed
sys.path.append(str(project_root))
from src.register_context.domain.value_objects.password import Password  # Adjust this import to your actual file structure

def test_valid_password():
    """Test valid password creation."""
    valid_password = Password(value="Valid1Password!")
    assert valid_password.value == "Valid1Password!"  # Assert the password matches the input

def test_password_too_short():
    """Test password that's too short (less than 8 characters)."""
    with pytest.raises(ValueError, match="Password must be at least 8 characters long."):
        Password(value="Short1!")
        
def test_password_missing_uppercase():
    """Test password missing an uppercase letter."""
    with pytest.raises(ValueError, match="Password must contain at least one uppercase letter (A-Z)."):
        Password(value="nouppercase1!")
        
def test_password_missing_lowercase():
    """Test password missing a lowercase letter."""
    with pytest.raises(ValueError, match="Password must contain at least one lowercase letter (a-z)."):
        Password(value="NOLOWERCASE1!")
        
def test_password_missing_digit():
    """Test password missing a numeric digit."""
    with pytest.raises(ValueError, match="Password must contain at least one numeric digit (0-9)."):
        Password(value="NoDigitHere!")
        
def test_password_missing_special_character():
    """Test password missing a special character."""
    with pytest.raises(ValueError, match="Password must contain at least one special character (e.g., !@#$%^&*)."):
        Password(value="NoSpecialChar1")
        
def test_password_with_special_characters():
    """Test password that satisfies all conditions."""
    valid_password = Password(value="Valid1Password@")
    assert valid_password.value == "Valid1Password@"  # Assert valid password is accepted

def test_password_not_string():
    """Test password is not a string."""
    with pytest.raises(TypeError, match="Password value must be a string, got int"):
        Password(value=12345678)  # Password is passed as an integer instead of a string

def test_password_empty():
    """Test empty password."""
    with pytest.raises(ValueError, match="Password must be at least 8 characters long."):
        Password(value="")  # Empty password should fail validation
