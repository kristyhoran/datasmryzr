import pytest
import os
from src.datasmryzr.utils import check_file_exists

@pytest.fixture
def temp_file():
    """Fixture to create a temporary file."""
    file_path = "temp_test_file.txt"
    with open(file_path, "w") as f:
        f.write("Temporary file content.")
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path)

def test_check_file_exists_file_exists(temp_file):
    """Test check_file_exists when the file exists."""
    assert check_file_exists(temp_file) is True

def test_check_file_exists_file_does_not_exist():
    """Test check_file_exists when the file does not exist."""
    assert check_file_exists("non_existent_file.txt") is False