"""
This module provides functions for processing pairwise distances between isolates,
including generating histograms and heatmaps for visualization.
"""

import pandas as pd
import pathlib
import altair as alt
from datasmryzr.utils import check_file_exists



def _get_distances(distances:str) -> pd.DataFrame:
    """
    Function to get the pairwise distances between isolates.
    Args:
        distances (str): Path to the distances file.
    Returns:
        pd.DataFrame: DataFrame containing the pairwise distances.
    """
    print(f"Getting distances from {distances}")
    if not check_file_exists(distances):
        raise FileNotFoundError(f"Distance file {distances} does not exist.")

    
    distance = f"{pathlib.Path(distances)}"
    try:
        df = pd.read_csv(distance, sep = None, engine='python')
    
        names = list(df.columns[1:len(df.columns)])
        col1 = df.columns[0]
        
        melted_df = pd.melt(df, id_vars=[col1], value_vars=names)
        melted_df = melted_df[melted_df[col1]!= melted_df['variable']]
        melted_df = melted_df.rename(columns={col1: 'Isolate1'})
        melted_df = melted_df.rename(columns={'variable': 'Isolate2'})
        melted_df = melted_df.rename(columns={'value': 'Distance'})
        return melted_df
    except:
        print(f"Error reading the distance file: {distance}")
        raise SystemError
   

def _plot_histogram(distances:str,bar_color:str = '#216cb8') -> dict:
    """
    Function to plot the pairwise distances between isolates as a histogram.
    Args:
        distances (str): Path to the distances file.
    Returns:
        dict: Dictionary containing the plot data.
    """
    df = _get_distances(distances)
    try:
        
        chart = alt.Chart(df).mark_bar(color = f"{bar_color}").encode(
                            alt.X(
                                'Distance', 
                                axis = alt.Axis(
                                    title = 'Pairwise SNP distance'
                                    )
                                    ),
                            y=alt.Y(
                                'count()', 
                                axis= alt.Axis(
                                    title = "Frequency"
                                    )
                                    )
                        ).properties(
                                width=1200,
                                height=200
                            )
        chart = chart.to_json()
        return chart
    except Exception as e:
        print(f"Error generating histogram: {e}")
        return {}

def _plot_heatmap(distances:str) -> dict:
    """
    Function to plot the pairwise distances between isolates as a heatmap.
    Args:
        distances (str): Path to the distances file.
    Returns:
        dict: Dictionary containing the plot data.
    """
    df = _get_distances(distances)
    print(df)
    number_of_isolates = len(df['Isolate1'].unique())
    try:
        chart = alt.Chart(df).mark_rect().encode(
                            x=alt.X('Isolate1:O').title(""),
                            y=alt.Y('Isolate2:O').title(""),
                            tooltip = [
                                alt.Tooltip('Isolate1:O'), 
                                alt.Tooltip('Isolate2:O'), 
                                alt.Tooltip('Distance:Q')],
                            color=alt.Color('Distance:Q').scale( scheme = "lightorange", reverse= True),
                        ).properties(
                                width=25*number_of_isolates,
                                height=25*number_of_isolates
                            )
        chart = chart.to_json()
        return chart
    except Exception as e:
        print(f"Error generating histogram: {e}")
        return {}