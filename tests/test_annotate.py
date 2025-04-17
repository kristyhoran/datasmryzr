import pytest
import pandas as pd
import os
import json
from datasmryzr.annotate import construct_annotations, _open_file, _get_cols, _get_colors, _make_legend, _get_metadata_tree
from datasmryzr.utils import check_file_exists

@pytest.fixture
def sample_dataframe():
    """Fixture to create a sample DataFrame."""
    return pd.DataFrame({
        "ID": ["A", "B", "C"],
        "Category": ["X", "Y", "Z"],
        "Value": [1, 2, 3],
        "CFG": ["ST", "MSLT", "ST"]
    })

@pytest.fixture
def temp_csv_file(tmp_path, sample_dataframe):
    """Fixture to create a temporary CSV file."""
    file_path = tmp_path / "test_file.csv"
    sample_dataframe.to_csv(file_path, index=False)
    return str(file_path)

@pytest.fixture
def sample_config_file(tmp_path):
    """Fixture to create a sample configuration file."""
    config_file = tmp_path / "config.json"
    config_data = {
        "categorical_columns": ["Category", "CFG"]
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)
    return str(config_file)

def test_construct_annotations_with_valid_path(temp_csv_file, sample_config_file):
    """Test construct_annotations with a valid file path."""
    result = construct_annotations(
        path=temp_csv_file,
        cols=["Category", "CFG"],
        config=sample_config_file
    )
    assert "metadata_tree" in result
    assert "metadata_columns" in result
    assert "colors_css" in result
    assert "legend" in result
    assert len(result["metadata_columns"]) == 2
    assert len(result["metadata_tree"]) == 3

def test_construct_annotations_with_empty_path():
    """Test construct_annotations with an empty file path."""
    result = construct_annotations(
        path="",
        cols=["Category", "CFG"],
        config=""
    )
    assert result["metadata_tree"] == {}
    assert result["metadata_columns"] == []
    assert result["colors_css"] == {}
    assert result["legend"] == []

def test_construct_annotations_invalid_config(temp_csv_file):
    """Test construct_annotations with an invalid configuration file."""
    with pytest.raises(FileNotFoundError):
        construct_annotations(
            path=temp_csv_file,
            cols=["Category", "CFG"],
            config="non_existent_config.json"
        )

def test_construct_annotations_invalid_columns(temp_csv_file, sample_config_file):
    """Test construct_annotations with invalid columns."""
    with pytest.raises(ValueError):
        construct_annotations(
            path=temp_csv_file,
            cols=["InvalidColumn"],
            config=sample_config_file
        )