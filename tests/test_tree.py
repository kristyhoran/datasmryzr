import pytest
import os
from src.datasmryzr.tree import _get_tree_string

@pytest.fixture
def sample_tree_file(tmp_path):
    """Fixture to create a sample tree file."""
    tree_file = tmp_path / "sample_tree.nwk"
    with open(tree_file, "w") as f:
        f.write("(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);")
    return str(tree_file)

def test_get_tree_string_valid_file(sample_tree_file):
    """Test _get_tree_string with a valid tree file."""
    tree_string = _get_tree_string(sample_tree_file)
    assert tree_string == "(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);"

def test_get_tree_string_empty_path():
    """Test _get_tree_string with an empty file path."""
    tree_string = _get_tree_string("")
    assert tree_string == ""

def test_get_tree_string_file_not_found():
    """Test _get_tree_string with a non-existent file."""
    tree_string = _get_tree_string("non_existent_file.nwk")
    assert tree_string == ""