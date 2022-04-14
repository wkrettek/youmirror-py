__all__ = [""]

'''
This module manages the filetree
------
This is the second most important module in the project, it must be able to 
generate the paths and filenames that make up the project with the given options
and resolve any naming conflicts. Thankfully, we can do most of our work with just
pathlib and some crafty organization
# TODO
I am deciding between two filetree implementations
Let's call this the 'tall' implementation
   Root
    | -- channels
            | -- channel name
                    | -- videos
                    | -- captions
                    | -- audio
                    | -- thumbnails
    | -- playlists
            | -- playlist name
                    | -- videos
                    | -- captions
                    | -- audio
                    | -- thumbnails
    | -- singles
            | -- videos
            | -- captions
            | -- audio
            | -- thumbnails

----- or -----
Lets' call this the 'wide' implementation
   Root
    | -- videos
            | -- channels
                    | -- channel name
            | -- playlists
                    | -- playlist name
            | -- singles
    | -- captions
            | -- channels
            | -- playlists
            | -- singles
    | -- audio
            | -- channels
            | -- playlists
            | -- singles
    | -- thumbnails
            | -- channels
            | -- playlists
            | -- singles
------------------
The second one is better for the stuff I want to do with this project later on (files of the same type are all under one tree),
but the first one is better for keeping things more condensed. And if you just download videos, like most people do, you'll just see one folder inside the root, which is always annoying AF to me
------------------
I think I can implement an "export" command later on to use the db to export things that are grouped together. Sucks if your db gets corrupted, but oh well
'''

import youmirror.parser as parser
from pathlib import Path
import logging
from typing import Union


def get_path(path : str, filename : str) -> Path:
    '''
    Wraps a path and filename into a Path object
    '''
    path = Path(path)   # Wrap the path
    filepath = path/Path(filename)
    return filepath

def file_exists(filepath: Path) -> bool:
    '''
    Checks if the config exists in the current working directory
    '''
    try:
        return filepath.is_file()              # Check if the file exists
    except Exception as e:
        logging.info(f"Could not check file {filepath} due to {e}")
        return False

def create_file(filepath: Path) -> None:
    '''
    Creates a file given a path and filename
    '''
    try:
        if not filepath.is_file():
            filepath.open(mode = "w")
    except Exception as e:
        print(e)

def create_path(path: Path) -> None:
    '''
    Creates the path 
    '''
    try:
        if not path.is_dir():
            path.mkdir(parents = True, exist_ok = True)     
    except Exception as e:
        print(e)

def calculate_path(file_type: str, parent_type: str, parent_name, yt_id: str) -> str:
    '''
    Calculates the filepath from the given database settings and returns a string
    wide formula = /file_type/parent_type/parent_name
    tall formula = /parent_type/parent_name/file_type
    '''
    file_types = {"videos", "captions", "audio", "thumbnails"}  # Valid file types
    parent_types = {"channels", "playlists", "singles"}         # Valid parent types
    path = Path(file_type)/Path(parent_type)/Path(parent_name)  # Build the filepath
    # TODO Resolve collision, need to add some handling here in case it sees a duplicate
    # path = resolve_collision(path, yt_id)
    return  str(path)

# TODO
def resolve_collision(path: Path, yt_id: str) -> Path:
    '''
    Appends the yt_id if the path already exists
    This could cause a lot of issues if we're not careful. I think committing
    all changes to the db at once will solve this
    ---- This is gonnna be super hard ----
    '''
    if path.exists():                           # If the path already exists
        path = Path(str(path) + f'_ym{yt_id}' ) # Append "_ym{yt_id}" to the end of the name 
    return path

def calculate_filename(name: str, extension: str) -> str:
    '''
    Determines the filename from the name and extension
    '''
    try:
        filename = name + extension
        # filename = resolve_collision()
        return filename
    except Exception as e:
        return None

def verify_installation(filepath: Path) -> bool:
    '''
    Take a database entry and verify that it is fully installed
    '''
    logging.info(f"Checking if file {filepath}")
    if filepath.is_file():
        logging.info(f"File {filepath} is installed")
        return True
    else:
        logging.info(f"File {filepath} is not installed")
    return False

