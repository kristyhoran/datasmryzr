import pytest
import pandas as pd
import pathlib
import gzip
import os
from src.datasmryzr.core_genome import (
    _get_offset,
    get_bin_size,
    check_masked,
    get_contig_breaks,
    _read_vcf,
    _get_vcf,
    _plot_snpdensity,
)
from src.datasmryzr.utils import check_file_exists

@pytest.fixture
def sample_reference_file(tmp_path):
    """Fixture to create a sample reference genome file."""
    reference_file = tmp_path / "reference.fasta"
    with open(reference_file, "w") as f:
        f.write(">contig1\n" + "A" * 10000 + "\n>contig2\n" + "T" * 5000)
    return str(reference_file)

@pytest.fixture
def sample_vcf_file(tmp_path):
    """Fixture to create a sample VCF file."""
    vcf_file = tmp_path / "sample.vcf"
    with open(vcf_file, "w") as f:
        f.write(
            "##fileformat=VCFv4.2\n"
            "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSample1\n"
            "contig1\t100\t.\tA\tT\t.\tPASS\t.\tGT\t1\n"
            "contig1\t200\t.\tA\tG\t.\tPASS\t.\tGT\t1\n"
        )
    return str(vcf_file)

@pytest.fixture
def sample_mask_file(tmp_path):
    """Fixture to create a sample mask file."""
    mask_file = tmp_path / "mask.txt"
    with open(mask_file, "w") as f:
        f.write("contig1\t50\t150\n")
    return str(mask_file)

def test_get_offset(sample_reference_file):
    """Test _get_offset function."""
    contig_info, total_length = _get_offset(sample_reference_file)
    assert isinstance(contig_info, dict)
    assert total_length == 15000
    assert "contig1" in contig_info
    assert contig_info["contig1"]["length"] == 10000

def test_get_bin_size():
    """Test get_bin_size function."""
    contig_info = {
        "contig1": {"length": 10000},
        "contig2": {"length": 5000},
    }
    max_bins = get_bin_size(contig_info)
    assert max_bins == 3  # Total length is 15000, so 15000 / 5000 = 3

def test_check_masked(sample_mask_file, sample_vcf_file):
    """Test check_masked function."""
    contig_info = {
        "contig1": {"offset": 0, "length": 10000},
    }
    df = pd.DataFrame({"index": [100, 200], "vars": [1, 2]})
    masked_df = check_masked(sample_mask_file, df, contig_info)
    assert "mask" in masked_df.columns
    assert masked_df.loc[masked_df["index"] == 100, "mask"].values[0] == "masked"

def test_get_contig_breaks():
    """Test get_contig_breaks function."""
    contig_info = {
        "contig1": {"offset": 0, "length": 10000},
        "contig2": {"offset": 10000, "length": 5000},
    }
    breaks = get_contig_breaks(contig_info)
    assert len(breaks) == 1  # Only contig1 exceeds 5000 bp

def test_read_vcf(sample_vcf_file):
    """Test _read_vcf function."""
    lines = _read_vcf(sample_vcf_file)
    assert len(lines) == 3  # Header + 2 data lines
    assert lines[1].startswith("contig1")

def test_get_vcf(sample_vcf_file):
    """Test _get_vcf function."""
    df = _get_vcf(sample_vcf_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2  # Two rows of data
    assert "#CHROM" in df.columns

def test_plot_snpdensity(sample_reference_file, sample_vcf_file, sample_mask_file):
    """Test _plot_snpdensity function."""
    chart = _plot_snpdensity(
        reference=sample_reference_file,
        vcf_file=sample_vcf_file,
        mask_file=sample_mask_file,
    )
    assert isinstance(chart, str)  # Altair chart is returned as JSON
    assert "Core genome position" in chart