"""
This module provides functions for generating metadata annotations
and legends for a DataFrame, mapping metadata variables to colors.
"""
import pandas as pd
import json
from mycolorpy import colorlist as mcp
from datasmryzr import utils



def _open_file(file_path:str) -> pd.DataFrame:
    """
    Open a file and return its contents.
    Args:
        file_path (str): Path to the file.
    Returns:
        str: File contents.
    """
    df = pd.read_csv(file_path, sep = None, engine = 'python')
    return df
    

def _check_vals(df:pd.DataFrame, 
                cols:list,
                cfg:dict) -> list:
    """
    Validates and filters the specified columns from a DataFrame based on 
    their data type and configuration settings.
    Args:
        df (pd.DataFrame): The input DataFrame to check.
        cols (list): A list of column names to validate.
        cfg (dict): A configuration dictionary containing the key 
            'categorical_columns', which specifies columns to treat as 
            categorical.
    Returns:
        list: A list of valid column names that are either non-numerical or 
        explicitly specified as categorical in the configuration.
    Raises:
        ValueError: If none of the specified columns are valid or if none of 
        the columns exist in the DataFrame.
    """
                
    final_cols = []
    _id_col = df.columns[0]
    indf = False
    for col in cols:
        if col in df.columns:
            indf = True
            is_string = True
            if col != _id_col:
                
                for val in df[col].unique():
                    if isinstance(val, str):   
                        is_string = True
                    else: 
                        is_string = False
                    
                if is_string or col in cfg['categorical_columns']:
                    final_cols.append(col)
    if not final_cols:
        if indf:
            raise ValueError(
                f"Columns {', '.join(cols)} do not contain any valid values.\
                 Please check the column names."
            )
        raise ValueError(
            f"None of the columns {', '.join(cols)} are in the dataframe or \
            in the correct format - only non-numerical data can be included. \
            Please check the column names."
        )
    else:
        return final_cols


def _get_cols(cols: list, df: pd.DataFrame, cfg: dict) -> list:
    """
    Retrieve and validate a list of columns from a DataFrame based on the 
    provided configuration.
    Args:
        cols (list): A list of column names to retrieve or the string "all" 
        to select all columns.
        df (pd.DataFrame): The DataFrame from which columns will be retrieved.
        cfg (dict): A configuration dictionary used for validation.
    Returns:
        list: A list of validated column names.
    Notes:
        - If `cols` is "all", all columns in the DataFrame will be selected 
        and validated.
        - The `_check_vals` function is used to validate the selected columns 
        against the configuration.
    """
              
    if cols == "all":
        return _check_vals(df=df, cols=df.columns.tolist(), cfg=cfg)
    return _check_vals(df=df, cols=cols, cfg=cfg)


def _get_colors(df:pd.DataFrame, 
                cols:list) -> tuple:
    """
    Generate a dictionary of CSS-compatible color mappings for unique values
    in specified columns of a DataFrame.
    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        cols (list): A list of column names in the DataFrame for which 
        unique values will be assigned colors.
    Returns:
        tuple: A dictionary where keys are modified color names 
        (CSS-compatible) and values are the corresponding color codes.
    """
    
    colors_set: set = set()
    colors_css: dict = {}

    for col in cols:
        unique_vals = list(df[col].unique())
        length = len(unique_vals)
        colors = mcp.gen_color(cmap="tab20b", n=length)
        colors_set.update(colors)

    for cl in colors_set:
        nme = cl.replace("#", "a")
        if nme not in colors_css:
            colors_css[nme] = cl
    return colors_css


def _make_legend(df:pd.DataFrame, 
                 cols:list, 
                 color_css:dict) -> dict:
    """
    Generate a legend mapping unique values in specified columns of a 
    DataFrame to corresponding colors from a given CSS color dictionary.

    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        cols (list): A list of column names in the DataFrame to generate 
        legends for.
        color_css (dict): A dictionary where keys are color names or codes, 
                            and values are CSS color definitions.

    Returns:
        dict: A dictionary where each key is a column name from `cols`, and
        the value is a list of dictionaries mapping unique column values 
        to colors.

    Notes:
        - Values equal to "NA" are excluded from the legend.
        - If the number of unique values in a column exceeds the number of 
        available colors in `color_css`, only the first `len(color_css)` 
        unique values are mapped.
    """
    legend: dict = {}
    for col in cols:
        unique_vals = [val for val in df[col].unique() if val != "NA"]
        colors = list(color_css.keys())
        cols_mapped = zip(unique_vals, colors)
        legend[col] = [{val: color} for val, color in cols_mapped]
    return legend

def _get_metadata_tree(df:pd.DataFrame, 
                       cols:list, 
                       legend: dict, 
                       color_css:dict) -> dict:
    """
    Generate a metadata structure from a DataFrame.
    This function creates a nested dictionary (metadata tree) where each key corresponds to a unique value 
    in the first column of the DataFrame (`tiplabel`). For each row in the DataFrame, the metadata tree 
    includes additional metadata for specified columns (`cols`), with associated color and label information.
    Args:
        df (pd.DataFrame): The input DataFrame containing the data to process. The first column is used as 
                            the primary key (`tiplabel`) for the metadata.
        cols (list): A list of column names from the DataFrame to include in the metadata.
        legend (dict): A dictionary mapping column names to dictionaries that map column values to colors.
                        Example: { "column_name": { "value1": "color1", "value2": "color2" } }.
        color_css (dict): A dictionary mapping color names to CSS-compatible color codes.
                            Example: { "red": "#FF0000", "blue": "#0000FF" }.
    Returns:
        dict: A nested dictionary representing the metadata. Each key corresponds to a unique value 
                in the first column of the DataFrame, and each value is a dictionary containing metadata 
                for the specified columns, including color and label information.
    Example:
        Input DataFrame:
            +---------+--------+--------+
            | tiplabel| col1   | col2   |
            +---------+--------+--------+
            | A       | value1 | value2 |
            | B       | value3 | value4 |
            +---------+--------+--------+
        cols = ["col1", "col2"]
        legend = {
            "col1": {"value1": "red", "value3": "blue"},
            "col2": {"value2": "green", "value4": "yellow"}
        color_css = {"red": "#FF0000", "blue": "#0000FF", "green": "#00FF00", "yellow": "#FFFF00"}
        Output:
        {
            "A": {
                "col1": {"colour": "#FF0000", "label": "value1"},
                "col2": {"colour": "#00FF00", "label": "value2"}
            },
            "B": {
                "col1": {"colour": "#0000FF", "label": "value3"},
                "col2": {"colour": "#FFFF00", "label": "value4"}
    """
    
    metadata_tree = {}
    tiplabel = df.columns[0]
    
    for _, row in df.iterrows():
        metadata_tree[row[tiplabel]] = {
            col: {
                "colour": color_css.get(
                    next(
                        (lg[row[col]] for lg in legend[col] if row[col] in lg),
                        "white",
                    ),
                    "white",
                ),
                "label": row[col],
            }
            for col in cols
            if col != tiplabel
        }
    return metadata_tree

    

def construct_annotations(path: str, 
                          cols: list,
                          config:str) -> dict:
    """
    Constructs annotations based on the provided file path and columns.
    This function processes a file to generate metadata annotations, including
    a metadata tree, metadata columns, CSS color mappings, and a legend. If no
    file path is provided, it returns default empty structures.
    Args:
        path (str): The file path to the data source. If empty, default values
            are returned.
        cols (list): A list of column names to be used for generating metadata.
    Returns:
        dict: A dictionary containing the following keys:
        - "metadata_tree" (dict): A hierarchical representation of metadata.
        - "metadata_columns" (list): A list of metadata column names.
        - "colors_css" (dict): A mapping of metadata values to CSS color codes.
        - "legend" (list): A list of legend entries for the metadata.
    """    
    if not path:
        return {
            "metadata_tree": {},
            "metadata_columns": [],
            "colors_css": {},
            "legend": [],
        }

    df = _open_file(path).fillna("NA")
    cfg = utils.get_config(config)
    metadata_columns = _get_cols(cols=cols, df=df, cfg=cfg)
    colors_css = _get_colors(df=df, cols=metadata_columns)
    legend = _make_legend(df=df, cols=metadata_columns, color_css=colors_css)
    metadata_tree = _get_metadata_tree(
        df=df, cols=metadata_columns, legend=legend, color_css=colors_css
    )
    return {
        "metadata_tree": metadata_tree,
        "metadata_columns": metadata_columns,
        "colors_css": colors_css,
        "legend": legend,
    }

