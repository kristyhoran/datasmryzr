import pathlib
import json
import pandas as pd

def check_file_exists(file_path: str) -> bool:
    """
    Check if a file exists at the given path.

    Args:
        file_path (str): Path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return pathlib.Path(file_path).exists()


def get_config(file_path: str) -> dict:
    """
    Get the configuration from a file.

    Args:
        file_path (str): Path to the configuration file.

    Returns:
        dict: Configuration data.
    """
    with open(file_path, 'r') as _file:
        config = json.load(_file)
    return config

def _open_df(file_path: str) -> pd.DataFrame:
    """
    Open a CSV file and return it as a DataFrame.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the data from the CSV file.
    """
    if not check_file_exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    df = pd.read_csv(file_path, sep=None, engine="python")
    return df


def _get_pangenome_acc(_dtype:str)-> dict:
    
    print(f"Getting pangenome colors for {_dtype} type")
    colors = {
        "basic" :{
            "domain":["Core","Intermediate","Rare"],
            "_range":["#3182bd", "#3f007d", "#228a44"]
        },
        "detail":{
            "domain":["Lineage specific core","Multi-lineage core", "Collection core","Lineage specific intermediate",
             "Multi-lineage intermediate","Collection intermediate","Lineage specific rare", "Multi-lineage rare" ,
             "Collection rare", "Intermediate and rare","Core, intermediate and rare","Core and rare", "Core and intermediate",
             "Absent in labelled lineages"],
             "_range":['#c6dbef', '#6baed6', '#3182bd',
                 '#dadaeb', '#9e9ac8', '#3f007d',
                 '#c7e9c0', '#73c476', '#228a44',
                 '#fedfc0', '#fdb97d', '#fd8c3b', '#e95e0d', 
                 '#d9d9d9']
        }
    }
    # print(colors[_dtype])
    orders = {
        "detail":{
            "Lineage specific core":3,
            "Multi-lineage core":2, 
            "Collection core":1,
            "Lineage specific intermediate":3,
            "Multi-lineage intermediate":2,
            "Collection intermediate":1,
            "Lineage specific rare":3, 
            "Multi-lineage rare" :2,
            "Collection rare":1,
            "Intermediate and rare":5,
            "Core, intermediate and rare":4,
            "Core and rare":3, 
            "Core and intermediate":2,
            "Absent in labelled lineages":1
        },
        "basic":{
            "Core":3, 
            "Intermediate":2,
            "Rare":1
            }
    }
    # print(orders[_dtype])
    return [colors[_dtype],orders[_dtype]]