"""
This module provides functions for processing configuration files, determining file delimiters,
checking numeric columns, and generating dictionaries with metadata.
"""

import json
import csv
from datasmryzr.utils import check_file_exists



def _get_config(path:str) -> dict:
    """
    Load the configuration file.
    Args:
        path (str): Path to the configuration file.
    Returns:
        dict: Configuration dictionary.
    Raises:
        FileNotFoundError: If the configuration file does not exist.
    """
    if not check_file_exists(path):
        raise FileNotFoundError(f"Configuration file {path} not found.")
    with open(path, 'r') as f:
        cfg = json.load(f)
    
    return cfg

def _get_delimiter(file:str) -> str:
    """
    Function to get the delimiter of a file.
    Args:
        file (str): Path to the file.
    Returns:
        str: Delimiter used in the file.
    Raises:
        ValueError: If the delimiter cannot be determined.
    """
    with open(file, "r", encoding="utf-8") as f:
        line = f.read()
        if "\t" in line:
            return "\t"
        if "," in line:
            return ","
        raise ValueError(f"Unknown delimiter in file: {file}")


def _check_numeric(col:str, 
                   data:list) -> bool:
    
    """
    Determines if all values in a specified column of a dataset can be
    converted to numeric.
    Args:
        col (str): The name of the column to check.
        data (list): A list of dictionaries representing the dataset, 
        where each dictionary 
                        corresponds to a row and contains column-value pairs.
    Returns:
        bool: Returns "number" if all values in the specified column can 
        be converted to numeric, otherwise returns "input".
    """

    is_numeric = set()
    for row in data:
        try:
            float(row[col])
            is_numeric.add(True)
        except ValueError:
            is_numeric.add(False)
    return "number" if len(is_numeric)==1 and True in is_numeric else "input"

        
def generate_table(_file :str, 
                   table_dict:dict, 
                   col_dict:dict,
                   comment_dict:dict, 
                   cfg_path:str) -> dict:
    """
    Generates a table representation from a given file and updates the provided 
    dictionaries with table, column, and comment information.
    Args:
        _file (str): The path to the input file containing data to be processed.
        table_dict (dict): A dictionary to store table metadata and data. 
        If empty, it will be initialized.
        col_dict (dict): A dictionary to store column metadata for the table. 
        If empty, it will be initialized.
        comment_dict (dict): A dictionary to store comments associated with the table. 
        If empty, it will be initialized.
        cfg_path (str): The path to the configuration file containing metadata
        such as comments and data types.
    Returns:
        tuple: A tuple containing the updated 
        `table_dict`, `col_dict`, and `comment_dict`.
    Raises:
        FileNotFoundError: If the input file does not exist.
        KeyError: If required keys are missing in the configuration file.
    """

    cfg = _get_config(cfg_path)
    dlm = _get_delimiter(_file)
    if not check_file_exists(_file):
        raise FileNotFoundError(f"Input file {_file} does not exist.")

    with open(_file, 'r') as f:
        reader = csv.DictReader(f, delimiter = dlm)
        data = [row for row in reader]
        columns = list(reader.fieldnames)
    title = _file.split('/')[-1].split('.')[0].replace('_', ' ').replace('-', ' ')
    link = title.replace(' ', '-').replace('_', '-').lower()
    comment = cfg["comments"].get(link, "")
    comment_dict[link] = comment_dict.get(link, comment)

    if link not in table_dict:
        print(f"Creating table for {title}")
        table_dict[link] = {"link": link, "name": title, "tables": []}

    if link not in col_dict:
        col_dict[link] = []
    
    _id =1
    
    for col in columns:
        _type = cfg["datatype"].get(col, _check_numeric(col=col, data=data))
        d ={
            'title':col,
            'field':col,
            'headerFilter':_type,
            'headerFilterPlaceholder':f'Search {col}'
        }
        if _type == 'number':
            d['headerFilterFunc'] = ">="
            d['headerFilterPlaceholder'] = f'At least...'    
        col_dict[link].append(d)
 
    for row in data:
        _sample_dict = {"id":_id}
        _id = _id + 1
        for col in columns:
            _sample_dict[col] = f"{row[col]}"
        table_dict[link]['tables'].append(_sample_dict)

    return table_dict,col_dict,comment_dict