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
    _id_col = df.columns[0]
    for col in cols:
        if col not in df.columns:
            raise ValueError(f"Column {col} not found in dataframe.")
        is_string = True
        # print(col)
        if col != _id_col:
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
    if cols == "all":
        column_list = _check_vals(df = df, cols = df.columns.tolist())
        return column_list
    else:
        column_list = _check_vals(df = df, cols = cols)
        if len(column_list) == 0:
            raise ValueError(f"None of the columns {', '.join( cols )} are in the dataframe or in the correct format - only non numerical data can be included. Please check the column names.")
        return column_list



def _get_colors(df:pd.DataFrame, cols:list) -> tuple:
    
    """
    Generate a dictionary of CSS-compatible color mappings for unique values in specified columns of a DataFrame.
    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        cols (list): A list of column names in the DataFrame for which unique values will be assigned colors.
    Returns:
        tuple: A dictionary where keys are modified color names (CSS-compatible) and values are the corresponding color codes.
    """
    
    colors_set = set()
    colors_css = {}
    
    

    # setup the css dict first and legend dict
    for col in cols:
        unique_vals = list(df[col].unique())
        length = len(unique_vals)
        colors = mcp.gen_color(cmap="tab20b", n=length)
        # colors_list = random.shuffle(list(colors))
        colors_set = set(colors_set).union(set(colors))

    # setup the css dict        
    for cl in colors_set:
        nme = cl.replace("#", "a")
        if nme not in colors_css:
            colors_css[nme] = cl
    # print(colors_css)
    return colors_css


def _make_legend(df:pd.DataFrame, cols:list, color_css:dict) -> dict:
   
    """
    Generate a legend mapping unique values in specified columns of a DataFrame 
    to corresponding colors from a given CSS color dictionary.

    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        cols (list): A list of column names in the DataFrame to generate legends for.
        color_css (dict): A dictionary where keys are color names or codes, 
                            and values are CSS color definitions.

    Returns:
        dict: A dictionary where each key is a column name from `cols`, and the value 
                is a list of dictionaries mapping unique column values to colors.

    Notes:
        - Values equal to "NA" are excluded from the legend.
        - If the number of unique values in a column exceeds the number of available 
            colors in `color_css`, only the first `len(color_css)` unique values are mapped.
    """
    legend = {}
    for col in cols:
        unique_vals = list(df[col].unique())
        unique_vals = [val for val in unique_vals if val != "NA"]
        length = len(unique_vals)
        colors = list(color_css.keys())
        cols_mapped = zip(unique_vals, colors)
        if col not in legend:
            legend[col] = [] 
        for val, color in cols_mapped:      
            lg = {
                val:color
            }
        legend[col].append(lg)
    return legend

def _get_metadata_tree(df:pd.DataFrame, cols:list, legend: dict, color_css:dict) -> dict:
    
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
    
    for row in df.iterrows():
        metadata_tree[row[1][tiplabel]] = {}

        for col in cols:

            if col == tiplabel:
                continue
            
            color = "white"
            
            for lg in legend[col]:
                if row[1][col] in lg:
                    color = lg[row[1][col]]
            metadata_tree[row[1][tiplabel]][col] = {
                "colour": color_css[color] if color in color_css else color,
                "label": row[1][col]
            }
    return metadata_tree
    

def construct_annotations(path:str, cols:list) -> dict:
    """
    Constructs a metadata annotation structure based on the provided file path and columns.
    This function processes a file to extract metadata information, assigns colors to unique 
    categorical values, and generates a metadata tree, legend, and associated CSS color styles.
    Args:
        path (str): The file path to the data source. If an empty string is provided, 
                    an empty metadata structure is returned.
        cols (list): A list of column names to be used for metadata extraction.
    Returns:
        dict: A dictionary containing the following keys:
            - "metadata_tree" (dict): A hierarchical representation of the metadata.
            - "metadata_columns" (list): A list of columns containing metadata information.
            - "colors_css" (dict): A mapping of unique values to their assigned CSS colors.
            - "legend" (list): A legend describing the metadata and associated colors.
    Notes:
        - The function assumes that the file at the given path can be opened and processed 
            into a DataFrame.
        - Missing values in the data are replaced with the string "NA".
        - Helper functions `_open_file`, `_get_cols`, `_get_colors`, `_make_legend`, and 
            `_get_metadata_tree` are used to perform specific tasks.
    """

    if path != "":
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
    else:
        data = {
            "metadata_tree": {},
            "metadata_columns": [],
            "colors_css": {},
            "legend": []
        }
    return data

    