
import pandas as pd
import numpy as np
import pathlib
import altair as alt
import json
import csv
from datasmryzr.utils import check_file_exists


def _get_config(path:str) -> dict:
    """
    Function to get the configuration file.
    Args:
        path (str): Path to the configuration file.
    Returns:
        dict: Configuration dictionary.
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
    """
    with open(file, 'r') as f:
        line = f.read()
        # print(line)
        if '\t' in line:
            return '\t'
        elif ',' in line:
            return ','
        else:
            raise ValueError("Unknown delimiter") 
        

def _check_numeric(col:str, data:list) -> bool:
    
    """
    Determines if all values in a specified column of a dataset can be converted to numeric.
    Args:
        col (str): The name of the column to check.
        data (list): A list of dictionaries representing the dataset, where each dictionary 
                        corresponds to a row and contains column-value pairs.
    Returns:
        bool: Returns "number" if all values in the specified column can be converted to numeric,
                otherwise returns "input".
    """

    number = set()
    
    for row in data:
        
        try:
            float(row[col])
            n = True
        except:
            n = False
        
        number.add(n)
    if len(number) == 1 and True in number:
        return "number"
    else:
        return "input"
        
def generate_table(_file :str, table_dict:dict, col_dict:dict,comment_dict:dict, cfg_path:str) -> dict:
    
    """
    Generates a table representation from a given file and updates the provided dictionaries with table, column, 
    and comment information.
    Args:
        _file (str): The path to the input file containing data to be processed.
        table_dict (dict): A dictionary to store table metadata and data. If empty, it will be initialized.
        col_dict (dict): A dictionary to store column metadata for the table. If empty, it will be initialized.
        comment_dict (dict): A dictionary to store comments associated with the table. If empty, it will be initialized.
        cfg_path (str): The path to the configuration file containing metadata such as comments and data types.
    Returns:
        tuple: A tuple containing the updated `table_dict`, `col_dict`, and `comment_dict`.
    Notes:
        - The function reads the input file, extracts its data, and generates metadata for tables and columns.
        - It uses the configuration file to determine data types and comments for the table.
        - If the input dictionaries are empty, they will be initialized and populated with the generated data.
        - The function assumes the input file is in CSV format and uses the appropriate delimiter.
    Raises:
        FileNotFoundError: If the input file does not exist.
        KeyError: If required keys are missing in the configuration file.
    """

    cfg = _get_config(cfg_path)
    dlm = _get_delimiter(_file)
    if check_file_exists(_file):
        with open(_file, 'r') as f:
            reader = csv.DictReader(f, delimiter = dlm)
            data = [row for row in reader]
            columns = list(reader.fieldnames)
        title = _file.split('/')[-1].split('.')[0].replace('_', ' ').replace('-', ' ')
        link = title.replace(' ', '-').replace('_', '-').lower()
        if link in cfg['comments']:
            comment=  cfg['comments'][link]
        else:
            comment =  ""
        if comment_dict == {}:
            comment_dict = {link:comment}
        else:
            comment_dict[link] = comment
        if table_dict == {}:
            print(f"Creating table for {title}")
            table_dict = {link:
                {'link':link, 'name':title, 'tables':[]}
                }
        else:
            table_dict[link] = {'link':link, 'name':title, 'tables':[]}
        if col_dict == {}:
            col_dict = {link: []}
        else:
            col_dict[link] = []
        
        _id =1
        
        for col in columns:
            _type = cfg['datatype'][col] if col in cfg['datatype'] else _check_numeric(col = col, data = data)
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
    print(comment_dict)
    print(col_dict)
    print(table_dict)
    return table_dict,col_dict,comment_dict