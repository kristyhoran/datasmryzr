"""
This module provides functions for generating summary reports based on genomic data.
It includes functions for processing input files, generating visualizations, and rendering
a summary report using a Jinja2 template.
"""

from datasmryzr.annotate import construct_annotations
from datasmryzr.utils import check_file_exists, get_config
from datasmryzr.tables import generate_table
from datasmryzr.core_genome import _plot_snpdensity, _plot_stats
from datasmryzr.distances import _plot_histogram, _plot_heatmap
from datasmryzr.tree import _get_tree_string
from datasmryzr.pangenome import _pangenome_summary, do_pangenome_graph
from datasmryzr.summary import summary_graphs
from datasmryzr.clusters import get_cluster_table, get_cluster_graphs,get_cluster_distances

import pandas as pd
import pathlib
import jinja2
import datetime


def get_num_isos(filenames:list) -> int:

    """
    Calculates the number of unique identifiers (isos) from a list 
    of CSV files.

    This function reads a list of file paths, checks if each file 
    exists, and processes the files to extract unique values from 
    the first column of each non-empty CSV file. The total count 
    of unique identifiers is returned.

    Args:
        filenames (list): A list of file paths to CSV files.

    Returns:
        int: The count of unique identifiers found across all valid files.

    Notes:
        - The function uses `pd.read_csv` with `sep=None` and `engine='python'` 
            to infer the delimiter automatically.
        - Only files that exist and contain at least one row are processed.
        - The first column of each file is used to extract unique values.
    """
    # print(filenames)
    unique_isos = set()
    for filename in filenames:
        if 'version' not in filename:
            if check_file_exists(filename):
                try:
                    df = pd.read_csv(filename, sep=None, engine="python")
                    # print(df)
                    if not df.empty:
                        for i in list(df.iloc[:, 0].unique()):
                            # print(f"Adding unique isolate: {i}")
                            unique_isos.add(i)
                except Exception as e:
                    print(f"Error processing file {filename}: {e}")
        # print("UNIQUE ISOLATES: ", unique_isos)
    return len(unique_isos)

def _make_menu(config: str, filenames: list, tree:str) -> list:
    
    cfg = get_config(file_path = config)

    menu_dflt = cfg.get("menu", [])
    
    
    if tree == "" and tree in menu_dflt:
        menu_dflt.remove("tree")
    
    
    # print(menu)
    tmp = []
    for _file in filenames:
        title = pathlib.Path(_file).stem.replace('_', ' ').replace('-', ' ')
        try:
            df = pd.read_csv(_file, sep='\t')
            tmp.append(title)
        except Exception as e:
            print(f"Error reading file {_file}: {e}")
    menu = []
    for m in menu_dflt:
        link = m.replace(' ', '-').replace('_', '-').lower()
        title = m.replace('_', ' ').replace('-', ' ')
        if title in tmp:
            d = {"link": link, "name": title}
            # print(d)
            menu.append(d)
    for title in sorted(tmp):
        # print(title)
        link = title.lower().replace(' ', '-')
        if link not in menu_dflt:
            print("not found : ", link)
            d = {"link": link, "name": title}
            menu.append(d)
    

    return menu


def _make_pangenome_graph(
    pangenome_rtab: str,
    pangenome_characterization: str = "",
    pangenome_groups: str = ""
):
    """
    Generate a pangenome graph based on the provided pangenome data.

    Args:
        pangenome_rtab (str): Path to the gene presence/absence Rtab file.
        pangenome_characterization (str): Path to the pangenome characterization file.
        pangenome_groups (str): Path to the pangenome groups file.

    Returns:
        dict: A dictionary containing the pangenome graph data.
    """
    if pangenome_rtab != "":
        return do_pangenome_graph(
            pangenome_rtab = pangenome_rtab,
            pangenome_characterization = pangenome_characterization,
            groups = pangenome_groups
        )
    else:
        return {}

def make_density_plot(
    core_genome: str,
    reference: str,
    mask: str,
    background_color: str
):
    
    """
    Generate a density plot for SNPs based on the provided core genome VCF 
    file and reference genome.
    Args:
        core_genome (str): Path to the core genome VCF file. 
        Must not be an empty string.
        reference (str): Path to the reference genome file. 
        Must not be an empty string.
        mask (str): Path to the mask file to exclude certain 
        regions from the analysis.
        background_color (str): Color to use for the background 
        of the density plot.
    Returns:
        dict: A dictionary containing the SNP density plot data if 
        both `core_genome` and `reference` are provided. Returns an empty 
        dictionary if either `core_genome` or `reference` is an empty string.
    """
    print("Generating SNP density plot...")
    if core_genome != "" and reference != "":
        return _plot_snpdensity(
            vcf_file = core_genome,
            reference = reference,
            mask_file = mask,
            bar_color = background_color,
        )
    else:
        return {}
def make_snp_heatmap(
    distance_matrix:str
):
    """
    Function to make a SNP heatmap.
    Args:
        distance_matrix (str): Path to the distance matrix file.
        reference (str): Path to the reference genome file.
        mask (str): Path to the mask file.
    Returns:
        dict: Dictionary containing the SNP heatmap data.
    """
    if distance_matrix != "" :
        return _plot_heatmap(
            distances = distance_matrix
        )
    else:
        return {}

def _make_summary_graph(
        config: str = "",
        bkg_color: str = "#343a40"
                    ) -> dict:
    """
    Generate a summary graph for pangenome data.

    Returns:
        dict: A dictionary containing the summary graph data.
    """
    # Placeholder for the summary graph data
    # This function can be expanded to include actual graph generation logic
    try:
        return summary_graphs( config=config)
    except Exception as e:
        print(f"Error generating summary graph: {e}")
        return {}

def make_snp_distances(
    distance_matrix:str,
    bar_color:str = "lightblue",
):
    """
    Function to make SNP distances.
    Args:
        distance_matrix (str): Path to the distance matrix file.
        reference (str): Path to the reference genome file.
        mask (str): Path to the mask file.
    Returns:
        dict: Dictionary containing the SNP distances data.
    """
    if distance_matrix != "":
        return _plot_histogram(
            distances = distance_matrix,
            bar_color=bar_color
        )
    else:
        return {}

def make_cluster_stats(
        distances:str,
        clusters:str,
        # bar_color:str = "lightblue",
):
    if distances != "" and clusters != "":
        return get_cluster_graphs(
            distances = distances,
            clusters = clusters,
            # bar_color=bar_color
        )
    else:
        return {}

def make_core_stats(
    core_genome_report:str,
    bar_color:str = "lightblue",
):
    """
    Function to make SNP distances.
    Args:
        distance_matrix (str): Path to the distance matrix file.
        reference (str): Path to the reference genome file.
        mask (str): Path to the mask file.
    Returns:
        dict: Dictionary containing the SNP distances data.
    """
    if core_genome_report != "":
        return _plot_stats(
            core_genome_report= core_genome_report,
            bar_color=bar_color
        )
    else:
        return {}

def _get_template(template:str) -> jinja2.Template:
    """
    Function to get the template.
    Args:
        template (str): Path to the template file.
    Returns:
        jinja2.Template: Jinja2 template object.
    """
    if check_file_exists(template):
        with open(template, "r", encoding="utf-8") as file:
            return jinja2.Template(file.read())
    raise FileNotFoundError(f"Template file {template} not found.")


def _get_target(outpath:str, title:str) -> str:
    
    """
    Generate the target file path for an HTML file based on the given 
    output path and title.

    Args:
        outpath (str): The directory path where the file should be saved.
        title (str): The title of the file, which will be used to generate
        the filename.

    Returns:
        str: The full path to the target HTML file.

    Raises:
        FileNotFoundError: If the specified output path does not exist.
    """

    if pathlib.Path(outpath).exists():
        name = f"{title.replace(' ', '_').replace(':', '_').replace('/', '_').lower()}.html"
        return pathlib.Path(outpath) / name
    raise FileNotFoundError(f"Output path {outpath} does not exist.")

def _parse_genome_file_name(filename:str) -> str:
    """
    Parse the genome file name to extract the base name without extension.

    Args:
        filename (str): The path to the genome file.

    Returns:
        str: The base name of the genome file without extension.
    """
    if filename == "":
        return ""
    return pathlib.Path(filename).stem.replace("_","-").replace(" ","-").lower()



def smryz(
        output: str, 
        title: str, 
        description: str, 
        author: str, 
        filename: list, 
        tree: str, 
        annotate: str, 
        annotate_cols: str, 
        distance_matrix: str, 
        cluster_table: str,
        core_genome: str, 
        core_genome_report: str,
        numvarsites: int,
        reference: str, 
        mask: str, 
        template: str, 
        background_color: str, 
        font_color: str,
        config: str,
        pangenome_rtab: str = "",
        pangenome_characterization: str = "",
        pangenome_groups: str = "",
        pipeline: str = "not provided",
        pipeline_version: str = "not provided",
        no_downloadable_tables: bool = False
) -> None:
    
    """
    Generates a summary report based on the provided data and configuration.
    Args:
    output (str): Path to save the generated summary report.
    title (str): Title of the summary report.
    description (str): Description of the summary report.
    author (str): Author of the report.
    filename (list): List of input file paths to process.
    tree (str): Path to the phylogenetic tree file in Newick format.
    annotate (str): Path to the annotation file.
    annotate_cols (str): Columns to use from the annotation file.
    distance_matrix (str): Path to the SNP distance matrix file.
    core_genome (str): Path to the core genome file.
    core_genome_report (str): Path to the core genome report file.
    reference (str): Path to the reference genome file.
    mask (str): Path to the mask file.
    template (str): Path to the template file for rendering the report.
    background_color (str): Background color for the report.
    font_color (str): Font color for the report.
    config (str): Path to the configuration file.
    Returns:
    None
    """

    print(f"Generating summary report for {title}...")
    print(f"Output will be saved to {output}")
    print(f"Using template {template}")
    print(f"Using configuration file {config}")
    tree_string = _get_tree_string(tree) 
    table_dict = {}
    col_dict = {}
    comments = {}
    
    filenames = [ i for i in filename if check_file_exists(i) ]
    
    if distance_matrix != "":
        filenames.append(distance_matrix)
    if core_genome_report != "":
        filenames.append(core_genome_report)
    if cluster_table != "" and distance_matrix != "":
        filenames.append(get_cluster_table(cluster_table, distance_matrix))
        # filenames.remove(cluster_table)
        filenames = [filename for filename in filenames if filename != cluster_table]
    print("Filenames to be processed: ", filenames)
    print(pangenome_groups)
    if pangenome_rtab != "":
        pangenome_summary = _pangenome_summary(
            pangenome_rtab = pangenome_rtab,
            pangenome_characterization = pangenome_characterization,
            groups = pangenome_groups
        )
        filenames.append(f"{pathlib.Path.cwd() / pangenome_summary}")
    menu = _make_menu(config, filenames, tree)
    for _file in filenames:
        print(f"Processing file {_file}...")
        try:
            table_dict, col_dict, comments = generate_table(
                _file = _file, 
                table_dict= table_dict, 
                col_dict=col_dict,
                comment_dict=comments, 
                cfg_path = config)
            print(f"File {_file} processed.")
        except Exception as e:
            print(f"Error processing file {_file}: {e}")
    
    metadata_dict = construct_annotations(
        path = annotate,
        cols = annotate_cols,
        config=config
    )
    data = {
        "title": title,
        "num_isos": get_num_isos(filename),
        "description": description,
        "background_color": background_color,
        "font_color": font_color,
        "date": f"{datetime.datetime.today().strftime('%Y-%m-%d')}",
        "user": author if author != "" else f"unknown",
        "phylo": "phylo" if tree != "" else "no_phylo",
        "menu":menu,
        "tables": table_dict,
        "columns": col_dict,
        "comment": comments,
        "distdict": get_cluster_distances(cluster_table, distance_matrix) if cluster_table != "" and distance_matrix != "" else {},
        "numvarsites": f"{numvarsites} variant sites used for tree construction" if numvarsites > 0 else "Number of variant sites not provided",
        "newick": tree_string,
        "core_genome": _parse_genome_file_name(core_genome_report),
        "snp_distances": make_snp_distances(
        distance_matrix = distance_matrix,
        bar_color = background_color
    ) ,
        "snp_heatmap": make_snp_heatmap(
        distance_matrix = distance_matrix
    ),
        "snp_density": make_density_plot(
        core_genome = core_genome,
        reference = reference,
        mask = mask,
        background_color = background_color,
    ),
        "pangenome": _make_pangenome_graph(
            pangenome_rtab = pangenome_rtab,
            pangenome_characterization = pangenome_characterization,
            pangenome_groups = pangenome_groups
        ),
        "summary_graph" : _make_summary_graph(
            config=config,
            bkg_color=background_color
            ),
        "core_stats": make_core_stats(
            core_genome_report = core_genome_report,
            bar_color = background_color
        ),
        "cluster_stats": make_cluster_stats(
            distances = distance_matrix,
            clusters = cluster_table,
            # bar_color = background_color
        ),
        "annotate": annotate,
        "pipeline_name": pipeline,
        "pipeline_version": pipeline_version,
        "metadata_tree": metadata_dict["metadata_tree"],
        "metadata_columns": metadata_dict["metadata_columns"],
        "colors_css": metadata_dict["colors_css"],
        "legend": metadata_dict["legend"],
        "download_prefix": f"{title.replace(' ', '_').replace(':', '_').replace('/', '_').lower()}",
        "no_downloadable_tables": 'true' if no_downloadable_tables else 'false'
       
       
    }
    print('true' if no_downloadable_tables else 'false')
    print(no_downloadable_tables)
    print(f"Loading template {template}...")
    template = _get_template(template)
    target = _get_target(output, title)
    print(data["title"])
    print("Rendering template...")
    target.write_text(template.render(data))