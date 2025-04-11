import os
import pathlib


def _get_tree_string(tree_file):
    """
    Get the tree string from the tree file.
    Args:
        tree_file (str): Path to the tree file.
    Returns:
        str: Tree string.
    """
    tree_file = pathlib.Path(tree_file) # Convert to Path object
    if tree_file.exists():
        with open(f"{tree_file}", 'r') as t:
            tree = t.read().strip()
    else:
        tree = ''
    
    return tree




