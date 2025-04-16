import pytest
import pandas as pd
import os
import json
from src.datasmryzr.distances import _get_distances, _plot_histogram, _plot_heatmap
from src.datasmryzr.utils import check_file_exists

@pytest.fixture
def sample_distances_file(tmp_path):
    """Fixture to create a sample distances file."""
    distances_file = tmp_path / "distances.tsv"
    with open(distances_file, "w") as f:
        f.write(
            "Seqname\tIsolateA\tIsolateB\tIsolateC\n"
            "IsolateA\t0\t5\t10\n"
            "IsolateB\t5\t0\t15\n"
            "IsolateC\t10\t15\t0\n"
        )
    return str(distances_file)

def test_get_distances(sample_distances_file):
    """Test _get_distances function."""
    df = _get_distances(sample_distances_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 6  # 3 isolates, excluding diagonal
    assert "Isolate1" in df.columns
    assert "Isolate2" in df.columns
    assert "Distance" in df.columns

def test_get_distances_file_not_found():
    """Test _get_distances with a non-existent file."""
    with pytest.raises(FileNotFoundError, match="Distance file non_existent_file.tsv does not exist."):
        _get_distances("non_existent_file.tsv")

def test_plot_histogram(sample_distances_file):
    """Test _plot_histogram function."""
    chart = _plot_histogram(sample_distances_file)
    assert isinstance(chart, str)  # Altair chart is returned as JSON
    chart_dict = json.loads(chart)
    assert "mark" in chart_dict
    assert chart_dict["mark"] == {'color': '#216cb8', 'type': 'bar'}

def test_plot_histogram_invalid_file():
    """Test _plot_histogram with an invalid file."""
    with pytest.raises(FileNotFoundError, match="Distance file non_existent_file.tsv does not exist."):
        _plot_histogram("non_existent_file.tsv")

def test_plot_heatmap(sample_distances_file):
    """Test _plot_heatmap function."""
    chart = _plot_heatmap(sample_distances_file)
    assert isinstance(chart, str)  # Altair chart is returned as JSON
    chart_dict = json.loads(chart)
    assert "mark" in chart_dict
    assert chart_dict["mark"] == {'type': 'rect'}

def test_plot_heatmap_invalid_file():
    """Test _plot_heatmap with an invalid file."""
    with pytest.raises(FileNotFoundError, match="Distance file non_existent_file.tsv does not exist."):
        _plot_heatmap("non_existent_file.tsv")