"""
This module provides functions for processing configuration files, determining file delimiters,
checking numeric columns, and generating dictionaries with metadata.
"""

import json
import csv
import ast
import pathlib
from datasmryzr.utils import check_file_exists, get_config



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
    if "json" in file:
        return "json"
    with open(file, "r", encoding="utf-8") as f:
        line = f.read()
        if "\t" in line:
            return "\t"
        if "," in line:
            return ","
    return None

def _get_json_data(_file:str,
                   id_col:None) -> dict:
    """
    Function to read a JSON file and return its content as a dictionary.
    Args:
        file (str): Path to the file.
    Returns:
        dict: Dictionary representing the content of the JSON file.
    """
    with open(_file, 'r') as f:
        json_str = f.read()
        data = ast.literal_eval(json_str)
        # tmp_data = data[0]
        print(data)
        columns = set()
        for row in data:
            print(row)
            if "_children" in row:
                # print("Children found")
                for child in row["_children"]:
                    for key in child.keys():
                        if key != "_children":
                            columns.add(key)
            
        # else:
        if id_col:
            columns = sorted(columns,key=lambda x: [id_col].index(x) if x in [id_col] else 10e99)
    
        #     raise ValueError(f"Invalid JSON format in file: {_file}")
    return data,columns

def get_width(_file:str) -> int:
    pass

def _get_tabular_data(_file:str, dlm:str) -> list:
    """
    Function to read a tabular file and return its content as a list of dictionaries.
    Args:
        file (str): Path to the file.
        dlm (str): Delimiter used in the file.
    Returns:
        list: List of dictionaries representing the rows in the file.
    """
    with open(_file, 'r') as f:
        reader = csv.DictReader(f, delimiter = dlm)
        data = [row for row in reader]
        columns = list(reader.fieldnames)
        # print(data)
    return data,columns

def _decide_type(val:str,
                 is_numeric:set) -> str:
    """
    Function to determine the type of a value.
    Args:
        val (str): The value to be checked.
    Returns:
        str: The type of the value ("number" or "input").
    """
    try:
        float(val)
        is_numeric.add(True)
    except ValueError:
        is_numeric.add(False)
    return is_numeric

def _check_numeric(col:str, 
                   data:list,
                   is_json:bool = False) -> bool:
    
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
        if not is_json:
            val = row[col] 
            is_numeric = _decide_type(val, is_numeric)
        else:
            for sub in row["_children"]:
                # print(sub[col])
                val = sub[col]
                is_numeric = _decide_type(val, is_numeric)
                    
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
    is_json = False
    cfg = get_config(cfg_path)
    # print(cfg)
    dlm = _get_delimiter(_file)
    
    id_col = cfg["id_column"] if "id_column" in cfg else None
    # print(f"ID col:{id_col}")
    if not check_file_exists(_file):
        raise FileNotFoundError(f"Input file {_file} does not exist.")
    # print(dlm)
    if dlm != "json" and dlm is not None:
        data, columns = _get_tabular_data(_file, dlm)
    elif dlm == "json":
        data,columns = _get_json_data(_file, id_col=id_col)
        is_json = True

        
    title = pathlib.Path(_file).stem.replace('_', ' ').replace('-', ' ')
    link = pathlib.Path(_file).stem.replace(' ', '-').replace('_', '-').lower()
    comment = cfg["comments"].get(link, "")
    # print(comment)
    comment = "<br>".join(comment) if isinstance(comment, list) else comment
    # print(comment)
    comment_dict[link] = comment_dict.get(link, comment)

    if link not in table_dict:
        print(f"Creating table for {title}")
        table_dict[link] = {"link": link, "name": title, "tables": []}
    
    if link not in col_dict:
        col_dict[link] = []
    
    # try:
    if dlm:
        for col in columns:
            if col != "_children":
                _type = cfg["datatype"].get(col, _check_numeric(col=col, data=data, is_json=is_json))
                width = max(len(col) * 10, 120)
                d ={
                    'title':col,
                    'field':col,
                    'headerFilter':_type,
                    'headerFilterPlaceholder':f'Search {col}',
                    'formatter':"textarea",
                    "cssClass":"italic-column" if "Species" in col else "",
                    # "minWidth": f"{width if width > 50 else 50}px",
                }
                if _type == 'number':
                    d['headerFilterFunc'] = ">="
                    d['headerFilterPlaceholder'] = f'At least...'  
                if col == "Data assessment":
                    d["formatter"] = "traffic"
                    d["formatterParams"]={
                                            "min":0,
                                            "max":1,
                                            "color":["#ed671f","#3a9c4a"],
                                        }
                col_dict[link].append(d)
        _id =1
        for row in data:
            _sample_dict = {"id":_id}
            
            if not is_json:
                for col in columns:
                    _sample_dict[col] = f"{row[col]}" 
            else:
                if id_col:
                    _sample_dict[id_col] = f"{row[id_col]}" if id_col in row else None
                for col in columns:
                    _sample_dict[col] = f"{row[col]}" if col in row else ""
                _sample_dict["_children"] = []
                for sub in row["_children"]:
                    _id = _id + 1
                    _sub_sample_dict = {"id":_id}
                    for col in columns:
                        _sub_sample_dict[col] = f"{sub[col]}"
                    _sample_dict["_children"].append(_sub_sample_dict)
                    
            _id = _id + 1
            table_dict[link]['tables'].append(_sample_dict)
            table_dict[link]['has_graph'] = 'true' if link in cfg["has_graph"] else 'false'
                # for i in table_dict[link]['tables']:
                #     if 'plasmid' in i:
                #         print(i)
    # except Exception as e:
    #     print(f"An error has occured reading {_file}: {e}")
    return table_dict,col_dict,comment_dict