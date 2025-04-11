import pathlib
import pandas as pd
from mycolorpy import colorlist as mcp
import random
from datasmryzr import utils

CFG= ["ST","MSLT"]

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

def _check_vals(df:pd.DataFrame, cols:list) -> list:
    """
    Check if the values in the dataframe are valid.
    Args:
        df (pd.DataFrame): Dataframe to check.
        cols (list): List of columns to check.
    Returns:
        bool: True if the values are valid, False otherwise.
    """
    final_cols = []
    for col in cols:
        is_string = True
        for val in df[col].unique():
            if isinstance(val, (int, float)):
                is_string = False
        if is_string or col in CFG:
            final_cols.append(col)
        
    return final_cols

def _get_cols(cols:list, df:pd.DataFrame) -> list:
    """
    Get the columns from the dataframe.
    Args:
        cols (list): List of columns to get.
        df (pd.DataFrame): Dataframe to get the columns from.
    Returns:
        list: a list of appropriate columns.
    """
    if cols == []:
        column_list = _check_vals(df = df, cols = df.columns.tolist())
        return column_list
    else:
        column_list = _check_vals(df = df, cols = cols)
        if len(column_list) == 0:
            raise ValueError(f"None of the columns {', '.join( cols )} are in the dataframe or in the correct format - only non numerical data can be included. Please check the column names.")
        return column_list



def _get_colors(df:pd.DataFrame, cols:list) -> tuple:
    """
    Assign colors to the columns in the dataframe.
    Args:
        df (pd.DataFrame): Dataframe to assign colors to.
        cols (list): List of columns to assign colors to.
    Returns:
        dict: Dictionary with the colors assigned to the columns.
    """
    colors_set = set()
    colors_css = {}
    
    

    # setup the css dict first and legend dict
    for col in cols:
        unique_vals = list(df[col].unique())
        length = len(unique_vals)
        colors = mcp.gen_color_list(length, cmap="tab20b")
        colors_list = random.shuffle(list(colors))
        colors_set = set(colors_set).union(set(colors))

    # setup the css dict        
    for cl in colors_set:
        nme = cl.replace("#", "")
        if nme not in colors_css:
            colors_css[nme] = cl

    return colors_css


def _make_legend(df:pd.DataFrame, cols:list, color_css:dict) -> dict:
    legend = []
    for col in cols:
        unique_vals = list(df[col].unique())
        length = len(unique_vals)
        colors = list(color_css.keys())[:length]
        cols_mapped = zip(unique_vals, colors)
        lg = {
            "category": col,
            "values": {}
        }
        for val, color in cols_mapped:
            if val != "NA":
             
                lg["values"]["color"] = color
                lg["values"]["label"] = val
                legend.append(lg)
    return legend

def _get_metadata_tree(df:pd.DataFrame, cols:list, legend: list, color_css:dict) -> dict:
            
    metadata_tree = {}
    tiplabel = df.columns[0]
    for row in df.iterrows():
        metadata_tree[row[1][tiplabel]] = {}

        for col in cols:

            if col == tiplabel:
                continue
            for lg in legend:
                if lg["category"] == col:
                    if row[1][col] != "NA":
                        metadata_tree[row[1][tiplabel]][col] = {
                            "color": color_css[lg["values"]["color"]],
                            "label": row[1][col]
                        }
                    else:
                        metadata_tree[row[1][tiplabel]][col] = {
                            "color": "white",
                            "label": row[1][col]
                        }
    return metadata_tree
    

def construct_annotations(path:str, cols:list) -> dict:
    
    df = _open_file(path)
    df = df.fillna("NA")
    # get columns that contain categorical data
    metadata_columns = _get_cols(cols = cols, df = df)
    #  get unique values and assign colors to them
    colors_css = _get_colors(df = df, cols = metadata_columns)
    # get the legend for the metadata
    legend = _make_legend(df = df, cols = metadata_columns, color_css = colors_css)
    # get the metadata tree
    metadata_tree = _get_metadata_tree(df = df, cols = metadata_columns, legend = legend, color_css = colors_css)
    # construct the final data structure
    data = {
        "metadata_tree": metadata_tree,
        "metadata_columns": metadata_columns,
        "colors_css": colors_css,
        "legend": legend
    }
    return data

    