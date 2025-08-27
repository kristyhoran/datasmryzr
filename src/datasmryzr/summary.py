"""
This module provides functions for processing pangenome files and generating visualisations
for pangenome analysis.
"""

import altair as alt
import pandas as pd
from Bio import SeqIO
import pathlib
import gzip
import csv
from datasmryzr.utils import check_file_exists, _open_df, get_config

alt.data_transformers.disable_max_rows()



def _get_dataframe(_path:str) -> pd.DataFrame:

    """
    Reads a CSV file containing pangenome groups.

    Args:
        _path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the pangenome groups.
    """
    if not check_file_exists(_path):
        raise FileNotFoundError(f"File not found: {_path}")
    
    df = _open_df(_path)
    return df


def _generate_summary_graphs(df:pd.DataFrame, facets: list, vals: list, bkg_color:str = "#343a40") -> dict:
    """
    Generates summary graphs for pangenome data.

    Args:
        df (pd.DataFrame): DataFrame containing pangenome data.
        facets (str): Column name to use for faceting the graphs.

    Returns:
        list: List of Altair charts representing the summary graphs.
    """
    fpres = False
    fac = ""
    for facet in facets:
        if facet in df.columns:
            fpres = True
            fac = facet
            break
    
    nums = []

    for val in vals:
        if val not in df.columns:
            print(f"Warning: {val} not found in the data.")
            continue        
        if fpres:
            chrt = alt.Chart(df, title = f"{val}").mark_bar(opacity=0.5).encode(
                x=alt.X(f"{val}:Q", bin=alt.Bin(maxbins=50)).title(val),
                y=alt.Y('count()').title("Count"),
                color=alt.Color(f'{fac}:O').title(f"{fac}").scale(scheme='viridis'),
            ).properties(
                width=1200,
                height=200
            )
        else:
            chrt = alt.Chart(df,title = f"{val}").mark_bar(opacity=0.5,color = f"{bkg_color}").encode(
                x=alt.X(f"{val}:Q", bin=alt.Bin(maxbins=50)).title(val),
                y=alt.Y('count()').title("Count"),
            ).properties(
                width=1200,
                
                height=200
            )
        nums.append(chrt)
    if not nums:

        return {}
    
    return alt.vconcat(*nums, spacing=10).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        grid=False,
        ).properties().to_json()



def summary_graphs(config:str, bkg_color:str = "#343a40")-> dict:
    """
    Generates summary graphs for pangenome data.

    Args:
        config (str): Path to the configuration file.

    Returns:
        dict: Dictionary containing the summary graphs.
    """
    config = get_config(config)
    _path = pathlib.Path(config["summary_graphs"]["summary_file"])
    facets = config["summary_graphs"]["facets"]
    vals = config["summary_graphs"]["vals"]

    df = _get_dataframe(_path)

    graph = _generate_summary_graphs(df, facets, vals, bkg_color)
    return graph