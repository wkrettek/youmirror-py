__all__ = [""]

'''
This module manages the filetree, I don't really know why it's called helper
but I like all the -er names for modules so here we are
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
                    | -- single name
                            | -- video file
                            | -- caption file
                            | -- audio file
                            | -- thumbnail file
    | -- playlists
            | -- playlist name
                    | -- single name
                            | -- video file
                            | -- caption file
                            | -- audio file
                            | -- thumbnail file
    | -- singles
            | -- single name
                    | -- video file
                        

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
I think for now I will implement the 'tall' implementation because it keeps things altogether. I may add an option to switch between the two later
------------------
I think I can implement an "export" command later on to use the db to export things that are grouped together. Sucks if your db gets corrupted, but oh well
'''
from pathlib import Path
import logging

valid_file_types = {"videos", "captions", "audio", "thumbnails"}  # Valid file types

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

def calculate_path(file_type: str, yt_type: str, parent_name) -> str:
    '''
    Calculates 
    wide formula = /file_type/yt_type/parent_name
    tall formula = /yt_type/parent_name/file_type
    '''
    # File type comes from options
    # Parent type comes from yt type
    # Parent name comes from yt name
    filetree_type = "tall"  # TODO THIS SHOULD BE PASSED FROM CONFIGS WHEN IMPLEMENTED
    yt_types = {"channel": "channels","playlist": "playlists", "single": "singles"}         # Valid parent types
    if yt_type in yt_types:             # Check the yt_type is valid
        yt_type = yt_types[yt_type]     # Yes I know this is dumb but I need to make it plural for formatting reasons
    if filetree_type == "tall":
        path = Path(yt_type)/Path(parent_name)/Path(file_type)  # Build the filepath
    else:
        path = Path(file_type)/Path(yt_type)/Path(parent_name)
    return  str(path)

def calculate_filename(file_type: str, yt_name: str) -> str:
    '''
    Calculates the filename from the given database settings and returns a string
    '''
    # File type comes from options
    # Parent type comes from yt type
    # Parent name comes from yt name
    file_type_to_extension = {"videos": ".mp4", "captions": ".srt", "audio": ".mp3", "thumbnails": ".jpg"}
    if file_type in valid_file_types:
        extension = file_type_to_extension[file_type]   # Convert the file type to an extension
        filename = f"{yt_name}{extension}"              # Add the name and extension together
        return filename
    else:
        logging.error(f"Invalid file type {file_type} passed") 

def calculate_filepath(file_type: str, yt_type: str, parent_name: str,  yt_name: str,) -> str:
    '''
    Calculates what filepaths apply to a given 
    '''
    path = calculate_path(file_type, yt_type, parent_name)
    filename = calculate_filename(file_type, yt_name)
    filepath = Path(path)/Path(filename)
    return str(filepath)

# TODO
def resolve_collision(path: str, filetree: dict, yt_id: str) -> str:
    '''
    Appends the yt_id if the path already exists
    '''
    if path in filetree:                        # If the path already exists
        logging.debug(f"Path {path} already exists")
        stem = Path(path).stem                  # Get the stem of the path
        suffix = Path(path).suffix              # Get the suffix of the path
        path = stem + f'_ym{yt_id}' + suffix    # Append "_ym{yt_id}" to the end of the name, reattach suffix 
    return path

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

