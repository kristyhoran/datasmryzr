"""
This module provides functions for processing VCF files, generating 
SNP density plots for core genome analysis.
"""

import altair as alt
import pandas as pd
import numpy as np
from Bio import SeqIO
import pathlib
import gzip
import csv
from datasmryzr.utils import check_file_exists

alt.data_transformers.disable_max_rows()

VCF_COLUMNS_TO_IGNORE = ['#CHROM', 
                         'POS', 
                         'ID', 
                         'REF', 
                         'ALT', 
                         'QUAL', 
                         'FILTER', 
                         'INFO', 
                         'FORMAT']

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
    Function to get the offset and length of each contig in the reference 
    genome.
    Args:
        reference (str): Path to the reference genome file.
    Returns:            
        tuple: Dictionary with contig information and total length of the 
        reference genome.
    """
    
    d = {}
    offset = 0
    records = list(SeqIO.parse(reference, "genbank"))
    if records == []:
        records = list(SeqIO.parse(reference, "fasta"))
    if records != []:
        for record in records:
            d[record.id.split('.')[0]] = {
                'offset' : offset, 
                'length': len(record.seq)
                }
            offset += len(record.seq)
    return d, offset

def get_bin_size(_dict:dict) -> int:
    """
    Calculate the maximum number of bins for SNP density plotting.

    Args:
        contig_dict (dict): Dictionary containing contig information.

    Returns:
        int: Maximum number of bins.
    """
    total_length = sum(contig['length'] for contig in _dict.values())
    max_bins = max(1, total_length // 5000)
    return max_bins

def check_masked(mask_file:str, 
                 df:pd.DataFrame, 
                 _dict:dict) -> pd.DataFrame:
    """
    Function to check if a mask file is used and if so, mask the regions 
    in the dataframe.
    Args:
        mask_file (str): Path to the mask file.
        df (pd.DataFrame): Dataframe containing the SNP data.
        _dict (dict): Dictionary containing the contig information.
    Returns:
        pd.DataFrame: Dataframe with masked regions.
    """

    masked = []
    if mask_file != '' and pathlib.Path(mask_file).exists():
        
        mask = pd.read_csv(f"{pathlib.Path(mask_file)}", 
                           sep = '\t', 
                           header = None, 
                           names = ['CHR','Pos1','Pos2'])
        mask['CHR'] = mask['CHR'].astype(str)
        
        for _, row in mask.iterrows():
            # print(row)
            offset = _dict[row['CHR']]['offset']
            masked.extend(
                range(row['Pos1'] + offset, row['Pos2'] + offset + 1)
                )
        
    df['mask'] = df['index'].apply(
                            lambda x: 'masked' if int(x) in masked else 'unmasked'
                          )
    
    return df

def get_contig_breaks(_dict:dict) -> list:
    """
    Function to get the contig breaks from a dictionary.
    Args:
        _dict (dict): Dictionary containing the contig information.
    Returns:
        list: List of contig breaks.
    """
    return [
        contig['length'] + contig['offset']
        for contig in _dict.values()
        if contig['length'] > 5000
    ]


def _read_vcf(vcf_file:str) -> str:
    """
    Function to read a VCF file and yield lines.
    Args:
        vcf_file (str): Path to the VCF file.
    Yields:
        str: Lines from the VCF file.
    """
    try:
        with gzip.open(vcf_file, 'rt') as f:
            return [line for line in f if not line.startswith('##')]
    except gzip.BadGzipFile:
        with open(vcf_file, 'r') as f:
            return [line for line in f if not line.startswith('##')]
    except Exception as e:
        raise SystemError(f"Error reading VCF file: {e}")

    
def _get_vcf(vcf_file:str) -> pd.DataFrame:
    """
    Function to read a VCF file and return a list of dictionaries.
    Args:
        vcf_file (str): Path to the VCF file.
    Returns:
        df: pd.DataFrame: Dataframe containing the VCF data.
    """
    reader = csv.reader(_read_vcf(vcf_file), delimiter='\t')
    header = next(reader)
    rows = list(reader)
    return pd.DataFrame(rows, columns=header)


def _get_ref_accession(reference: str) -> str:
    if pathlib.Path(reference).exists():
        acc = ""
        with open(reference, "r") as f:
            header = f.readline().strip().split("\n")[0]

        if header.startswith(">"):
            acc = header.strip(">")
        elif header.startswith("LOCUS"):
            acc = header.split(" ")[1]
        return acc
    return ""

def _plot_snpdensity(reference:str,
                     vcf_file:str, 
                     mask_file:str = '', 
                     bar_color:str = '#216cb8') -> alt.Chart:
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
    acc = _get_ref_accession(reference)
    chromosomes = list(_dict.keys())
    results = _get_vcf(vcf_file )    
    _maxbins = get_bin_size(_dict = _dict)
    vars = {}
    for result in results.iterrows():
        for chromosome  in chromosomes: 
                if chromosome not in vars: 
                    vars[chromosome] = {}
                if chromosome in result[1]["#CHROM"]: 
                    pos = int(result[1]["POS"]) 
                    for col in result[1].keys(): 
                        if col in VCF_COLUMNS_TO_IGNORE:
                            continue
                        if result[1][col] != '0': 
                            if pos not in vars[chromosome]: 
                                vars[chromosome][pos] = 1
                            else:
                                vars[chromosome][pos] = vars[chromosome][pos] + 1

    data = {}
    for var in vars:
        for pos in vars[var]:
            offset = _dict[var]['offset']
            data[pos + offset] = vars[var][pos]
    df = pd.DataFrame.from_dict(data, orient='index',columns=['vars']).reset_index()
    
    df = check_masked(mask_file = mask_file, df = df,_dict = _dict)
    
    for_contigs = get_contig_breaks(_dict = _dict)
    domain = ['masked', 'unmasked']
    range_ = ['#d9dcde', f"{bar_color}"]
    bar = alt.Chart(df).mark_bar(binSpacing=0).encode(
        x=alt.X('index:Q', bin=alt.Bin(maxbins=_maxbins), title = f"Core genome position (reference: {acc} ).", axis=alt.Axis(ticks=False)),
        y=alt.Y('vars:Q',title = "Variants observed per 5MB", axis=alt.Axis(ticks=False)),
        tooltip = [alt.Tooltip('index:Q', title = 'Position'), alt.Tooltip('sum(vars):Q', title = 'SNPs')],
        color=alt.Color('mask', scale = alt.Scale(domain=domain, range=range_), legend=None)
    )

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
    # print(chart)
    return chart

def _plot_stats(core_genome_report:str,
               bar_color:str = "#343a40") -> alt.Chart:
    """
    Function to plot the core genome statistics.
    Args:
        core_genome_stats (str): Path to the core genome statistics file.
    Returns:
        alt.Chart: Altair chart object.
    """
    if check_file_exists(core_genome_report):
        df = pd.read_csv(core_genome_report, sep='\t')
        df['% Not aligned'] = df['Unaligned'] / df['Length'] * 100
    
        cols = ['% Aligned','% Not aligned', 'Heterozygous',
       'Low coverage' ]
        
        charts = []
        for col in cols:
            if col in df.columns:
                df['jitter_x'] = df[f"{col}"].astype('category').cat.codes + np.random.uniform(-1000,10, len(df))
                box = alt.Chart(df).mark_boxplot(extent='min-max', opacity=.3, color = bar_color).encode(
                    x=alt.X(f"{col}:Q", sort=None),
                    # y='Value',
                    # color='Isolate'
                    
                ).properties(
                width=1200,
                # height=150
            )
                scatter = alt.Chart(df).mark_circle(size=80, color = bar_color).encode(
                    x=alt.X(f"{col}:Q"), # Hide axis for cleaner overlay
                    # Add jitter if desired (e.g., using a calculated jitter column or a transform)
                    yOffset='jitter_x:Q',
                    tooltip=['Isolate', f'{col}:Q'],
                ).properties(
                width=1200,
                # height=200
                )
                
                fig = box + scatter
                charts.append(fig)
        if charts != []:
            combined_chart = alt.vconcat(*charts).resolve_scale(
                    y='independent').configure_axis(
                                    grid=False
                    ).configure_view(
                    stroke=None
            )
            return combined_chart.to_json()
    return {}