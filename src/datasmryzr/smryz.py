from datasmryzr.annotate import construct_annotations
from datasmryzr.utils import check_file_exists
from datasmryzr.tables import generate_table
from datasmryzr.core_genome import _plot_snpdensity
from datasmryzr.distances import _plot_histogram, _plot_heatmap
from datasmryzr.tree import _get_tree_string

import pandas as pd
import pathlib, json, jinja2, datetime


# reporthtml = pathlib.Path(f'report_{args.pipeline}.html')
#     # # path to html template
#     indexhtml = pathlib.Path(args.template_dir,'index.html') 

def get_num_isos(filenames:list) -> int:

    """
    Calculates the number of unique identifiers (isos) from a list of CSV files.

    This function reads a list of file paths, checks if each file exists, and 
    processes the files to extract unique values from the first column of each 
    non-empty CSV file. The total count of unique identifiers is returned.

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

    dfs = []
    for filename in filenames:
        if check_file_exists(filename):
            df = pd.read_csv(filename, sep = None, engine = 'python')
            if df.shape[0] > 0:
                dfs.extend(df[df.columns.tolist()[0]].unique().tolist())
    dfs = list(set(dfs))
    return len(dfs)

def make_density_plot(
    core_genome: str,
    reference: str,
    mask: str,
    background_color: str
):
    
    """
    Generate a density plot for SNPs (Single Nucleotide Polymorphisms) based on the provided core genome VCF file 
    and reference genome.
    Args:
        core_genome (str): Path to the core genome VCF file. Must not be an empty string.
        reference (str): Path to the reference genome file. Must not be an empty string.
        mask (str): Path to the mask file to exclude certain regions from the analysis.
        background_color (str): Color to use for the background of the density plot.
    Returns:
        dict: A dictionary containing the SNP density plot data if both `core_genome` and `reference` are provided.
              Returns an empty dictionary if either `core_genome` or `reference` is an empty string.
    """
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
def make_snp_distances(
    distance_matrix:str
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
    
    """
    Generate the target file path for an HTML file based on the given output path and title.

    Args:
        outpath (str): The directory path where the file should be saved.
        title (str): The title of the file, which will be used to generate the filename.

    Returns:
        str: The full path to the target HTML file.

    Raises:
        FileNotFoundError: If the specified output path does not exist.
    """

    if pathlib.Path(outpath).exists():
        nme = f"{title.replace(' ', '_').replace(':', '_').replace('/', '_').lower()}.html"
        return  pathlib.Path(outpath) / nme
    else:
        raise FileNotFoundError(f"Output path {outpath} does not exist.")

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
        core_genome: str, 
        core_genome_report: str,
        reference: str, 
        mask: str, 
        template: str, 
        background_color: str, 
        font_color: str,
        config: str
):
    
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
    This function processes the input files, generates various visualizations and metadata, 
    and renders a summary report using the specified template. The report includes details 
    such as phylogenetic tree, SNP distances, SNP heatmap, SNP density plot, metadata, and 
    other relevant information.
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
    for _file in filenames:
        print(f"Processing file {_file}...")
        table_dict, col_dict, comments = generate_table(_file = _file, table_dict= table_dict, col_dict=col_dict,comment_dict=comments, cfg_path = config)
        print(f"File {_file} processed.")
    # print(comments)
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
        "tables": table_dict,
        "columns": col_dict,
        "comment": comments,
        "newick": tree_string,
        "snp_distances": make_snp_distances(
        distance_matrix = distance_matrix
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
    
        "metadata_tree": metadata_dict["metadata_tree"],
        "metadata_columns": metadata_dict["metadata_columns"],
        "colors_css": metadata_dict["colors_css"],
        "legend": metadata_dict["legend"],
       
       
    }
    
    # load the template
    print(f"Loading template {template}...")
    template = _get_template(template)
    target = _get_target(output, title)
    # render the template with the data
    print(f"Rendering template...")
    target.write_text(template.render(data))