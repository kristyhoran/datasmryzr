import click


@click.command()
@click.option('--filename', '-f', help = "Paths to tabular files for report generation. Multiple possible -f file1.csv -f file2.txt", multiple = True)
@click.option('--tree', '-t', help = "Paths tree file")
# @click.option('--annotate', '-a', help = "Path to tabular file that can be used to annotate trees (tree tiplabels must be first column). If --annotate_cols not used all columns in this file will be used.")
# @click.option('--annotate_cols', '-ac', help = "Comma separated list of columns to be used to annotate the tree. ", default = "all", type = str, show_default = True)
@click.option('--distance-matrix', '-dm', help="Specify the path to the file that can be used as a distance matrix to generate pairwise distance plots and heatmap.", type = str)
@click.option('--core-genome', '-cg', help="Specify the path to the file that can be used to generate a distribution of variants across a genome.", type = str)
@click.option('--reference', '-r', help="Specify the path to the reference file that can be used to generate a distribution of variants across a genome. Required if --core-genome is used.", type = str)

def smryz():
    """
    This is a small tool to generate a html and pdf files, collating and summarizing your pathogen genomics results tables and trees/networks.
    """
    print("Hello world")
if __name__ == '__main__':
    smryz()