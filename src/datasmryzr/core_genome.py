import altair as alt
import pandas as pd
import numpy as np
import pathlib
from Bio import SeqIO
import json
import gzip
import csv

from datasmryzr.utils import check_file_exists

alt.data_transformers.disable_max_rows()

VCF_COLUMNS_TO_IGNORE = ['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT']

def check_file_exists(file_path: str) -> bool:
    """
    Check if a file exists at the given path.

    Args:
        file_path (str): Path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return pathlib.Path(file_path).exists()

def _get_offset(reference:str) -> tuple:
    """
    Function to get the offset and length of each contig in the reference genome.
    Args:
        reference (str): Path to the reference genome file.
    Returns:            
        tuple: Dictionary with contig information and total length of the reference genome.
    """
    # print(reference)
    d = {}
    offset = 0
    records = list(SeqIO.parse(reference, "genbank"))
    if records == []:
        records = list(SeqIO.parse(reference, "fasta"))
    if records != []:
        for record in records:
            d[record.id.split('.')[0]] = {'offset' : offset, 'length': len(record.seq)}
            offset += len(record.seq)
    # print(d)
    return d, offset

def get_bin_size(_dict):

    sum_len = 0
    for d in _dict:
        sum_len = sum_len + _dict[d]['length']
    
    _maxbins = int(sum_len/5000)
    if _maxbins == 0:
        print(f"Something has gone wrong - the maxbins value should be > 0.")
    return _maxbins

def check_masked(mask_file:str, df:pd.DataFrame, _dict:dict) -> pd.DataFrame:
    """
    Function to check if a mask file is used and if so, mask the regions in the dataframe.
    Args:
        mask_file (str): Path to the mask file.
        df (pd.DataFrame): Dataframe containing the SNP data.
        _dict (dict): Dictionary containing the contig information.
    Returns:
        pd.DataFrame: Dataframe with masked regions.
    """

    masked = []
    if mask_file != '' and pathlib.Path(mask_file).exists():
        print('blocking out masked regions')
        mask = pd.read_csv(f"{pathlib.Path(mask_file)}", sep = '\t', header = None, names = ['CHR','Pos1','Pos2'])
        mask['CHR'] = mask['CHR'].astype(str)
        for row in mask.iterrows():
            # print(row[1])
            off = _dict[row[1]['CHR']]['offset']
            l = list(range(row[1]['Pos1'] + off, row[1]['Pos2']+off +1))
            masked.extend(l)

    df['mask'] = np.where(df['index'].isin(masked), 'masked', 'unmasked')
    
    return df

def get_contig_breaks(_dict:dict) -> list:
    """
    Function to get the contig breaks from a dictionary.
    Args:
        _dict (dict): Dictionary containing the contig information.
    Returns:
        list: List of contig breaks.
    """
    for_contigs = []
    for chromosome in _dict:
        if _dict[chromosome]['length'] > 5000:
            for_contigs.append(_dict[chromosome]['length'] + _dict[chromosome]['offset'])

    return for_contigs


def _read_vcf(vcf_file:str) -> str:
    """
    Function to read a VCF file and yield lines.
    Args:
        vcf_file (str): Path to the VCF file.
    Yields:
        str: Lines from the VCF file.
    """
    lines = []
    try:
        with gzip.open(vcf_file, 'rt') as f:
            for line in f:
                if not line.startswith('##'):
                    lines.append(line)
            return lines                   
    except gzip.BadGzipFile:
        with open(vcf_file, 'r') as f:
            for line in f:
                if not line.startswith('##'):
                    lines.append(line)
            return lines   
    except Exception as e:
        print(f"Error reading VCF file: {e}")
        print(f"Please check the file is a valid vcf file.")
       
        raise SystemError
    
def _get_vcf(vcf_file:str) -> pd.DataFrame:
    """
    Function to read a VCF file and return a list of dictionaries.
    Args:
        vcf_file (str): Path to the VCF file.
    Returns:
        df: pd.DataFrame: Dataframe containing the VCF data.
    """
    rows = []
    reader = csv.reader(_read_vcf(vcf_file), delimiter='\t')
    header = next(reader)
    for row in reader:
        rows.append(row)
    
    df = pd.DataFrame(rows, columns=header)
    return df



def _plot_snpdensity(reference:str,vcf_file:str, mask_file:str = '', bar_color:str = '#216cb8') -> alt.Chart:
    """
    Function to plot the SNP density across a genome.
    Args:
        reference (str): Path to the reference genome file.
        vcf_file (str): Path to the VCF file.
        mask_file (str): Path to the mask file. Default is ''.
    Returns:
        dict: Altair chart object.
    """


    for _file in [reference, vcf_file]:
        if not check_file_exists(_file):
            raise SystemError(f"File {_file} does not exist.")
    
    _dict,offset = _get_offset(reference = f"{pathlib.Path(reference)}")
    chromosomes = list(_dict.keys())
    results = _get_vcf(vcf_file )    
    _maxbins = get_bin_size(_dict = _dict)
    # collate all snps in snps.tab
    vars = {}
    for result in results.iterrows():
        # print(result)
        for chromosome  in chromosomes: #for each chromosome in the reference
                if chromosome not in vars: # if chromosome not in the dict create it
                    vars[chromosome] = {}
                if chromosome in result[1]["#CHROM"]: # if the chromosome in the result
                    # print(result[1]["#CHROM"])
                    pos = int(result[1]["POS"]) # get the position
                    for col in result[1].keys(): # for each isolate in the result
                        # print(col)
                        if col in VCF_COLUMNS_TO_IGNORE:# for each isolate in the result
                            continue
                        if result[1][col] != '0': # if the result is not 0
                            if pos not in vars[chromosome]: # increment the value of the postion
                                vars[chromosome][pos] = 1
                            else:
                                vars[chromosome][pos] = vars[chromosome][pos] + 1

    # # now generate list for x and y value in graph
    data = {}
    for var in vars:
        for pos in vars[var]:
            offset = _dict[var]['offset']
            data[pos + offset] = vars[var][pos]
    df = pd.DataFrame.from_dict(data, orient='index',columns=['vars']).reset_index()
    
    # check if mask file used - if yes grey it out in the graph.
    df = check_masked(mask_file = mask_file, df = df,_dict = _dict)
    # get positions of the contig breaks
    for_contigs = get_contig_breaks(_dict = _dict)
    # set colours
    domain = ['masked', 'unmasked']
    range_ = ['#d9dcde', f"{bar_color}"]
    # do bar graphs
    # if mask_file != 'no_mask':
    bar = alt.Chart(df).mark_bar(binSpacing=0).encode(
        x=alt.X('index:Q', bin=alt.Bin(maxbins=_maxbins), title = "Core genome position.", axis=alt.Axis(ticks=False)),
        y=alt.Y('vars:Q',title = "Variants observed per 5MB", axis=alt.Axis(ticks=False)),
        tooltip = [alt.Tooltip('index:Q', title = 'Position'), alt.Tooltip('sum(vars):Q', title = 'SNPs')],
        color=alt.Color('mask', scale = alt.Scale(domain=domain, range=range_), legend=None)
    )

    # generate list of graphs for addition of vertical lines
    graphs = [bar]
    if for_contigs != []:
        for line in for_contigs:
            graphs.append(alt.Chart().mark_rule(strokeDash=[3, 3], size=0.5, color = 'grey').encode(x = alt.datum(line)))
        
    chart = alt.layer(*graphs).configure_axis(
                    grid=False
                    ).properties(
                        width = 1200
                    ).interactive()

    chart = chart.to_json()
    
    return chart