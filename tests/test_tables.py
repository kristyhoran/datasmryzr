import pytest
import os
import json
import csv
from src.datasmryzr.tables import (
    _get_delimiter,
    _check_numeric,
    generate_table,
)
from src.datasmryzr.utils import check_file_exists

@pytest.fixture
def sample_config_file(tmp_path):
    """Fixture to create a sample configuration file."""
    config_file = tmp_path / "config.json"
    config_data = {
        "datatype": {
            "MLST":"input",
            "ST":"input"
            },
        "comments": {
            "data": "This is a sample table comment."
            }
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)
    return str(config_file)

@pytest.fixture
def sample_data_file(tmp_path):
    """Fixture to create a sample data file."""
    data_file = tmp_path / "data.csv"
    with open(data_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Column1", "Column2"])
        writer.writerow([1, "A"])
        writer.writerow([2, "B"])
        writer.writerow([3, "C"])
    return str(data_file)

def test_get_delimiter(sample_data_file):
    """Test _get_delimiter function."""
    delimiter = _get_delimiter(sample_data_file)
    assert delimiter == ","  # The sample file uses a comma as the delimiter

def test_get_delimiter_unknown_format(tmp_path):
    """Test _get_delimiter with an unknown format."""
    unknown_file = tmp_path / "unknown.txt"
    with open(unknown_file, "w") as f:
        f.write("Column1 Column2\n1 A\n2 B\n")
    with pytest.raises(ValueError, match="Unknown delimiter"):
        _get_delimiter(str(unknown_file))

def test_check_numeric():
    """Test _check_numeric function."""
    data = [{"Column1": "1"}, {"Column1": "2.5"}, {"Column1": "3"}]
    result = _check_numeric("Column1", data)
    assert result == "number"

    data = [{"Column1": "A"}, {"Column1": "B"}, {"Column1": "C"}]
    result = _check_numeric("Column1", data)
    assert result == "input"

def test_generate_table(sample_data_file, sample_config_file):
    """Test generate_table function."""
    table_dict, col_dict, comment_dict = generate_table(
        _file=sample_data_file,
        table_dict={},
        col_dict={},
        comment_dict={},
        cfg_path=sample_config_file
    )
    assert isinstance(table_dict, dict)
    assert isinstance(col_dict, dict)
    assert isinstance(comment_dict, dict)

    # Check table_dict structure
    assert "data" in table_dict
    assert "tables" in table_dict["data"]
    assert len(table_dict["data"]["tables"]) == 3  # 3 rows in the data file

    # Check col_dict structure
    assert "data" in col_dict
    assert len(col_dict["data"]) == 2  # 

    # Check comment_dict structure
    assert "data" in comment_dict
    assert comment_dict["data"] == "This is a sample table comment."