
import pandas as pd
import numpy as np
import pathlib
import altair as alt
import json
import csv
from datasmryzr.utils import check_file_exists

CFG = {
    "MLST":"input",
    "ST":"input"
}

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
        


# "file":"seqdata.txt", 
#             "title":"Sequence Data", 
#             "link": "sequence-data", 
#             "type" : "table",
#             "comment": "",
#             "columns" : [
#                 {"title":"Isolate","field":"Isolate","headerFilter":"input","headerFilterPlaceholder":"Search isolate"},
#                 {"title": "Reads", "field":"Reads","headerFilter":"number", "headerFilterPlaceholder":"at least...", "headerFilterFunc":">="},
#                 {"title":"Yield", "field":"Yield","headerFilter":"number", "headerFilterPlaceholder":"at least...", "headerFilterFunc":">="},
#                 {"title":"GC content", "field":"GC content","headerFilter":"number", "headerFilterPlaceholder":"at least...", "headerFilterFunc":">="},
#                 {"title":"Min len", "field":"Min len","headerFilter":"number", "headerFilterPlaceholder":"at least...", "headerFilterFunc":">="},
#                 {"title":"Avg len", "field":"Avg len","headerFilter":"number", "headerFilterPlaceholder":"at least...", "headerFilterFunc":">="},
#                 {"title":"Max len", "field":"Max len","headerFilter":"number", "headerFilterPlaceholder":"at least...", "headerFilterFunc":">="},
#                 {"title":"Average quality (% >Q30)", "field":"Average quality (% >Q30)","headerFilter":"number", "headerFilterPlaceholder":"at least...", "headerFilterFunc":">="},
#                 {"title":"Estimated average depth", "field":"Estimated average depth","headerFilter":"number", "headerFilterPlaceholder":"at least...", "headerFilterFunc":">="}
#                 ]

# {   "file": "distances.tab", 
#             "title":"SNP distances", 
#             "type":"matrix", 
#             "link":"snp-distances",
#             "comment": "",
#             "columns":[]
#         },



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
        
def _generate_table(_file :str) -> dict:
    
    dlm = _get_delimiter(_file)
    if check_file_exists(_file):
        with open(_file, 'r') as f:
            reader = csv.DictReader(f, delimiter = dlm)
            data = [row for row in reader]
            columns = list(reader.fieldnames)
        title = _file.split('/')[-1].split('.')[0].replace('_', ' ').replace('-', ' ')
        link = title.replace(' ', '-').replace('_', '-').lower()
        table_dict = {link:
            {'link':link, 'name':title, 'table':[]}
            }
        _id =1
        col_dict = {link: []}
        for col in columns:
            _type = CFG[col] if col in CFG else _check_numeric(col = col, data = data)
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

    return table_dict,col_dict