import pathlib
import json

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