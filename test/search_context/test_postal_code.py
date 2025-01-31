import pytest
import sys
from pathlib import Path
import os

project_root = Path(os.getcwd()).resolve().parent  # Adjust .parent if needed
sys.path.append(str(project_root))
from src.domain.value_objects.post_code import PostalCode

def test_valid_postal_code():
    """Test creation of a valid postal code."""
    postal_code = PostalCode(value="10115")
    assert postal_code.value == "10115"
    assert postal_code.is_valid()

def test_postal_code_invalid_format():
    """Test invalid postal code formats."""
    with pytest.raises(TypeError, match="Invalid postal code: 15123"):
        PostalCode(value="15123")  # Invalid due to prefix

    with pytest.raises(TypeError, match="Invalid postal code: 1000"):
        PostalCode(value="1000")  # Too few digits

    with pytest.raises(TypeError, match="Invalid postal code: 101151"):
        PostalCode(value="101151")  # Too many digits

def test_postal_code_non_numeric():
    """Test postal code with non-numeric characters."""
    with pytest.raises(TypeError, match=r"PostalCode must contain only numeric characters, got: 10A15"):
        PostalCode(value="10A15")
    
    with pytest.raises(TypeError, match=r"PostalCode must contain only numeric characters, got: ABCDE"):
        PostalCode(value="ABCDE")

def test_postal_code_not_a_string():
    """Test postal code with non-string input."""
    with pytest.raises(ValueError, match=r"PostalCode value must be a string, got int"):
        PostalCode(value=10115)  # Integer instead of string
    
    with pytest.raises(ValueError, match=r"PostalCode value must be a string, got list"):
        PostalCode(value=["10115"])  # List instead of string

def test_edge_case_postal_codes():
    """Test valid edge case postal codes."""
    postal_code_10 = PostalCode(value="10000")
    postal_code_14 = PostalCode(value="14999")
    assert postal_code_10.is_valid()
    assert postal_code_14.is_valid()
    assert postal_code_10.value == "10000"
    assert postal_code_14.value == "14999"

def test_postal_code_minimum_digits():
    """Test the exact minimum valid postal code."""
    postal_code = PostalCode(value="10000")
    assert postal_code.is_valid()
    assert postal_code.value == "10000"

def test_postal_code_maximum_digits():
    """Test the exact maximum valid postal code."""
    postal_code = PostalCode(value="14999")
    assert postal_code.is_valid()
    assert postal_code.value == "14999"

def test_postal_code_case_insensitive_pattern():
    """Ensure the regex pattern does not fail on valid input."""
    postal_code = PostalCode(value="10115")
    assert postal_code.is_valid()

def test_postal_code_with_whitespace():
    with pytest.raises(ValueError, match=r"Invalid postal code: 10115 "):
        PostalCode(value="10115 ")
    with pytest.raises(ValueError, match=r"Invalid postal code:  10115"):
        PostalCode(value=" 10115")
        
def test_empty_postal_code():
    with pytest.raises(ValueError, match=r"Invalid postal code: "):
        PostalCode(value="")

def test_international_postal_code():
    with pytest.raises(TypeError, match=r"Invalid postal code: 90210"):
        PostalCode(value="90210")  # Example: US ZIP Code



