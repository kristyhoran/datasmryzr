import click,pathlib, os, getpass, sys
from click.exceptions import UsageError
from click._compat import get_text_stderr
# from datasmryzr import __version__
from datasmryzr.smryz import smryz


@click.command(no_args_is_help=True)
@click.option('--output', '-o', help = "Path to the output directory where the report will be generated.", type = str, default = f"{pathlib.Path.cwd()}", show_default = True)
@click.option('--title', '-t', help = "Title of the report.", type = str, default = "Datasmryzr Report", show_default = True)
@click.option('--description', '-d', help = "Description of the report.", type = str, default = "This is a report generated by datasmryzr.", show_default = True)
@click.option('--author', '-a', help = "Author of the report.", type = str, default = f"{getpass.getuser()}", show_default = True)
@click.option('--filename', '-f', help = "Paths to tabular files for report generation. Multiple possible -f file1.csv -f file2.txt", multiple = True)
@click.option('--tree', '-tr', help = "Path tree file", default = "", type = str, show_default = True)
@click.option('--annotate', '-a', help = "Path to tabular file that can be used to annotate trees (tree tiplabels must be first column). If --annotate_cols not used all columns in this file will be used.",default = "", type = str, show_default = True)
@click.option('--annotate_cols', '-ac', help = "Comma separated list of columns to be used to annotate the tree. ", default = "all", type = str, show_default = True)
@click.option('--distance-matrix', '-dm', help="Specify the path to the file that can be used as a distance matrix to generate pairwise distance plots and heatmap.", type = str, default = "", show_default = True)
@click.option('--core-genome', '-cg', help="Specify the path to the file that can be used to generate a distribution of variants across a genome - a core.vcf file", type = str,default = "", show_default = True)
@click.option('--core-genome-report', '-cgr', help="Specify the path to the file that contaims core genome summary report - required for core genome graph", type = str,default = "", show_default = True)
@click.option('--reference', '-r', help="Specify the path to the reference file that can be used to generate a distribution of variants across a genome. Required if --core-genome is used.", type = str,default = "", show_default = True)
@click.option('--mask', '-m', help="Specify the path to the mask file that can be used to generate a distribution of variants across a genome. Required if --core-genome is used.", type = str,default = "", show_default = True)
@click.option('--template', '-tmpl', help="Specify the path to the template file", type = str, default = f"{pathlib.Path(__file__).parent}/templates/report.html.j2", show_default = True)
@click.option('--background_color', '-bg', help="Specify the background color of the report", type = str, default = "#546d78", show_default = True)
@click.option('--font_color', '-fc', help="Specify the font color of the report", type = str, default = "#ffffff", show_default = True)
@click.option('--config', '-c', help="Path to the config file", type = str, default = f"{pathlib.Path(__file__).parent / 'templates' / 'base_config.json'}", show_default = True)
@click.option('--version', '-v', is_flag=True, help="Show the version of datasmryzr.")
def smryzr(output:str, title:str, description:str, author:str, filename:list, tree:str, annotate:str, annotate_cols:str, distance_matrix:str, core_genome:str, reference:str, mask:str, template:str, background_color:str, font_color:str, config:str, version:bool, core_genome_report:str):
    """
    This is a small tool to generate a html and pdf files, collating and summarizing your pathogen genomics results tables and trees/networks.
    """
    print(tree)
    smryz(
        output = output,
        title = title,
        description = description,
        author = author,
        filename = filename,
        tree = tree,
        annotate = annotate,
        annotate_cols = annotate_cols,
        distance_matrix = distance_matrix,
        core_genome = core_genome,
        core_genome_report = core_genome_report,
        reference = reference,
        mask = mask,
        template = template,
        background_color = background_color,
        font_color = font_color,
        config = config,
    )
    


if __name__ == '__main__':



    smryzr()