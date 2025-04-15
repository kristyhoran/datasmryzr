
import pandas as pd
import numpy as np
import pathlib
import altair as alt
import json
from datasmryzr.utils import check_file_exists



# alt.Chart(df).mark_rect().encode(
#     x=alt.X('Isolate:O').title(""),
#     y=alt.Y('variable:O').title(""),
#     tooltip = [alt.Tooltip('Isolate:O'), alt.Tooltip('variable:O'), alt.Tooltip('value:Q')],
#     color=alt.Color('value:Q').scale( scheme = "lightorange", reverse= True),
# )

def _get_distances(distances:str) -> pd.DataFrame:
    """
    Function to get the pairwise distances between isolates.
    Args:
        distances (str): Path to the distances file.
    Returns:
        pd.DataFrame: DataFrame containing the pairwise distances.
    """
    if check_file_exists(distances):
        distance = f"{pathlib.Path(distances)}"
        try:
            df = pd.read_csv(distance, sep = '\t')
            # get a list of isolate names
            names = list(df.columns[1:len(df.columns)])
            col1 = df.columns[0]
            
            # if the there is no snp in the isolate (ie same as ref then mak na - then easy to drop)
            
            # collect positions to get allow for histogram and dropna (no snp)
            melted_df = pd.melt(df, id_vars=[col1], value_vars=names)
            melted_df = melted_df[melted_df[col1]!= melted_df['variable']]
            return melted_df
        except:
            print(f"Error reading the distance file: {distance}")
            raise SystemError
        
    else:
        print(f"Distance file {distance} does not exist.")
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
                            alt.X('value', axis = alt.Axis(title = 'Pairwise SNP distance')),
                            y=alt.Y('count()', axis= alt.Axis(title = "Frequency"))
                        ).properties(
                                width=1200,
                                height=200
                            )
        chart = chart.to_json()
        return chart
    except:
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
    number_of_isolates = len(df['Isolate'].unique())
    try:
        chart = alt.Chart(df).mark_rect().encode(
                            x=alt.X('Isolate:O').title(""),
                            y=alt.Y('variable:O').title(""),
                            tooltip = [alt.Tooltip('Isolate:O'), alt.Tooltip('variable:O'), alt.Tooltip('value:Q')],
                            color=alt.Color('value:Q').scale( scheme = "lightorange", reverse= True),
                        ).properties(
                                width=25*number_of_isolates,
                                height=25*number_of_isolates
                            )
        chart = chart.to_json()
        return chart
    except:
        return {}
