import pytest
import pandas as pd
import os
from src.datasmryzr.annotate import (
    _open_file,
    _check_vals,
    _get_cols,
    _get_colors,
    _make_legend,
    _get_metadata_tree,
    construct_annotations,
)

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
def temp_csv_file(sample_dataframe):
    """Fixture to create a temporary CSV file."""
    file_path = "test_file.csv"
    sample_dataframe.to_csv(file_path, index=False)
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path)

def test_open_file(temp_csv_file):
    df = _open_file(temp_csv_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3

def test_check_vals_valid_columns(sample_dataframe):
    result = _check_vals(sample_dataframe, ["Category", "CFG"])
    assert result == ["Category", "CFG"]

def test_check_vals_invalid_column(sample_dataframe):
    with pytest.raises(ValueError, match="Columns Value do not contain any valid values."):
        _check_vals(sample_dataframe, ["Value"])

def test_get_cols_all(sample_dataframe):
    result = _get_cols("all", sample_dataframe)
    assert result == ["Category","CFG"]

def test_get_cols_specific(sample_dataframe):
    result = _get_cols(["Category", "CFG"], sample_dataframe)
    assert result == ["Category", "CFG"]

def test_get_cols_no_valid_columns(sample_dataframe):
    with pytest.raises(ValueError, match="None of the columns InvalidColumn are in the dataframe"):
        _get_cols(["InvalidColumn"], sample_dataframe)

def test_get_colors(sample_dataframe):
    result = _get_colors(sample_dataframe, ["Category", "CFG"])
    assert isinstance(result, dict)
    assert len(result) > 0

def test_make_legend(sample_dataframe):
    colors_css = {"aX": "#FF0000", "aY": "#00FF00", "aZ": "#0000FF"}
    legend = _make_legend(sample_dataframe, ["Category"], colors_css)
    assert "Category" in legend
    assert len(legend["Category"]) == 3

def test_get_metadata_tree(sample_dataframe):
    colors_css = {"aX": "#FF0000", "aY": "#00FF00", "aZ": "#0000FF"}
    legend = _make_legend(sample_dataframe, ["Category"], colors_css)
    metadata_tree = _get_metadata_tree(sample_dataframe, ["Category"], legend, colors_css)
    assert "A" in metadata_tree
    assert "Category" in metadata_tree["A"]

def test_construct_annotations_with_path(temp_csv_file):
    result = construct_annotations(temp_csv_file, ["Category", "CFG"])
    assert "metadata_tree" in result
    assert "metadata_columns" in result
    assert "colors_css" in result
    assert "legend" in result

def test_construct_annotations_empty_path():
    result = construct_annotations("", ["Category", "CFG"])
    assert result["metadata_tree"] == {}
    assert result["metadata_columns"] == []
    assert result["colors_css"] == {}
    assert result["legend"] == []