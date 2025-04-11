
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
        line = f.readline()
        if '\t' in line:
            return '\t'
        elif ',' in line:
            return ','
        else:
            raise ValueError("Unknown delimiter") 
        

def _check_numeric(col:str, data:list) -> bool:
    number = set()
    
    for row in data:
        
        try:
            float(row[col])
            n = True
        except:
            n = False
        
        number.add(n)
    
    if len(number) == 1:
        return "number"
    else:
        return "input"
        
def generate_table(_file :str, table_dict:dict, col_dict:dict, cfg_path:str) -> dict:
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
            comment = cfg['comments'][link]
        else:
            comment = {}
        if table_dict == {}:
            table_dict = {link:
                {'link':link, 'name':title, 'table':[]}
                }
        else:
            table_dict[link] = {'link':link, 'name':title, 'table':[]}
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
            table_dict['table'].append(_sample_dict)

    return table_dict,col_dict,comment