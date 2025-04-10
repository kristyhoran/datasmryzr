import pathlib
import pandas as pd

from datasmryzr import utils


def _open_file(file_path):
    """
    Open a file and return its contents.
    Args:
        file_path (str): Path to the file.
    Returns:
        str: File contents.
    """
    df = pd.read_csv(file_path, sep = None, engine = 'python')
    return df

def _get_cols(cols:list, df:pd.DataFrame) -> list:
    """
    Get the columns from the dataframe.
    Args:
        cols (list): List of columns to get.
        df (pd.DataFrame): Dataframe to get the columns from.
    Returns:
        pd.DataFrame: Dataframe with the selected columns.
    """
    if cols == []:
        column_list = df.columns.tolist()[1:]
        return column_list
    else:
        column_list = [col for col in cols if col in df.columns.tolist()]
        if len(column_list) == 0:
            raise ValueError(f"None of the columns {cols} are in the dataframe. Please check the column names.")
        return column_list
    
def _get_metadata(df:pd.DataFrame, cols:list) -> dict:
    """
    Get the metadata from the dataframe.
    Args:
        df (pd.DataFrame): Dataframe to get the metadata from.
        cols (list): List of columns to get.
    Returns:
        dict: Dictionary with the metadata.
    """
    metadata = {}

    # col[0] is the first column, which is the tip label
    # col[1:] are the columns to be used as metadata
    # {
    #   col[0]{
    #       col[n]: {
    #        "color": colors,    },
    #       col[n+1]: { 
    #        "color": colors,    },
    #       col[n+2]: {
    #        "color": colors,    },
    # } is the metadata
    