from datasmryzr.annotate import construct_annotations
from datasmryzr.utils import check_file_exists
from datasmryzr.tables import generate_table
from datasmryzr.core_genome import _plot_snpdensity
from datasmryzr.distances import _plot_snp_distances, _plot_snp_heatmap
from datasmryzr.tree import _get_tree_string

import pandas as pd
import pathlib, json, jinja2, datetime


# reporthtml = pathlib.Path(f'report_{args.pipeline}.html')
#     # # path to html template
#     indexhtml = pathlib.Path(args.template_dir,'index.html') 

def get_num_isos(filenames:list) -> int:

    dfs = []
    for filename in filenames:
        if check_file_exists(filename):
            df = pd.read_csv(filename, sep = None, engine = 'python')
            if df.shape[0] > 0:
                dfs.extend(df[df.columns.tolist()[0]].unique().tolist())
    dfs = list(set(dfs))
    return len(dfs)

def make_density_plot(
    core_genome:str,
    reference:str,
    mask:str
):
    """
    Function to make a density plot.
    Args:
        core_genome (str): Path to the core genome file.
        reference (str): Path to the reference genome file.
        mask (str): Path to the mask file.
    Returns:
        dict: Dictionary containing the density plot data.
    """
    if core_genome != "" and reference != "":
        return _plot_snpdensity(
            core_genome = core_genome,
            reference = reference,
            mask = mask
        )
    else:
        return {}
def make_snp_heatmap(
    distance_matrix:str,
    reference:str,
    mask:str
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
    if distance_matrix != "" and reference != "":
        return _plot_snp_heatmap(
            distance_matrix = distance_matrix,
            reference = reference,
            mask = mask
        )
    else:
        return {}
def make_snp_distances(
    distance_matrix:str,
    reference:str,
    mask:str
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
    if distance_matrix != "" and reference != "":
        return _plot_snp_distances(
            distance_matrix = distance_matrix,
            reference = reference,
            mask = mask
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
        with open(template, 'r') as f:
            template = jinja2.Template(f.read())
        return template
    else:
        raise FileNotFoundError(f"Template file {template} not found.")

def _get_target(outpath:str, title:str) -> str:

    if pathlib.Path(outpath).exists():
        nme = f"{title.replace(' ', '_').replace(':', '_').replace('/', '_').lower()}.html"
        return f"{pathlib.Path(outpath)}/{nme}"
    else:
        raise FileNotFoundError(f"Output path {outpath} does not exist.")

def smryz(
        output:str, 
        title:str, 
        description:str, 
        author:str, 
        filename:list, 
        tree:str, 
        annotate:str, 
        annotate_cols:str, 
        distance_matrix:str, 
        core_genome:str, 
        reference:str, 
        mask:str, 
        template:str, 
        background_color:str, 
        font_color:str,
        config:str,
):
    

    tree_string = _get_tree_string(tree)
    table_dict = {}
    col_dict = {}
    for _file in filename:
        table_dict, col_dict, comments = generate_table(_file = _file, table_dict= table_dict, col_dict=col_dict, config_path = config)
    metadata_dict = construct_annotations(
        path = annotate,
        cols = annotate_cols,
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
        "table_dict": table_dict,
        "columns": col_dict,
        "comment": comments,
        "newick": tree_string,
        "snp_distances": make_snp_distances(
        distance_matrix = distance_matrix,
        reference = reference,
        mask = mask
    ) ,
        "snp_heatmap": make_snp_heatmap(
        distance_matrix = distance_matrix,
        reference = reference,
        mask = mask
    ),
        "snp_density": make_density_plot(
        core_genome = core_genome,
        reference = reference,
        mask = mask
    ),
    
        "metadata_tree": metadata_dict["metadata_tree"],
        "metadata_columns": metadata_dict["metadata_columns"],
        "colors_css": metadata_dict["colors_css"],
        "legend": metadata_dict["legend"],
       
       
    }
    # load the template

    template = _get_template(template)
    target = _get_target(output, title)
    # render the template with the data
    target.write_text(template.render(data))