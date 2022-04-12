__all__ = [""]

from pathlib import Path
import logging
import sys

def file_exists(path : str = "./", filename : str = "") -> bool:
    '''
    Checks if the config exists in the current working directory
    '''
    path = Path(path)                   # Wrap up the path
    filepath = path / Path(filename)    # Build the full path to the file
    try:
        return filepath.exists()              # Check if the file exists
    except Exception as e:
        logging.info(f"Could not check file {filepath} due to {e}")
        return False

def create_file(path: str, filename: str) -> None:
    '''
    Creates a file given a path and filename
    '''
    path = Path(path)                   # Wrap up the path
    filepath = path/Path(filename)      # Create full filepath
    try:
        filepath.open(mode = "w")
    except Exception as e:
        print(e)

def path_exists(path: str) -> bool:
    '''
    Checks if a path exists
    '''
    return Path(path).is_dir()

def create_path(path: str) -> None:
    '''
    Creates the path 
    '''
    try:
        path = Path(path)   # Wrap up the path
        path.mkdir(parents = True, exist_ok = True)
    except Exception as e:
        print(e)

def get_config(path : str) -> Path:
    '''
    Find the config file in the current working directory
    '''
    path = Path(path)   # Wrap the path
    filepath = path/Path('youmirror.json')
    if  filepath.exists():
        return filepath
    else:
        logging.error(f'Could not find config file in root {path}')
        sys.exit()
