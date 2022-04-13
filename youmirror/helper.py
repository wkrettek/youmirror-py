__all__ = [""]

# This module manages the file tree

import youmirror.parser as parser
from pathlib import Path
import logging
import sys
from pytube import Channel, Playlist, YouTube
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

def path_exists(path: Path) -> bool:
    '''
    Checks if a path exists
    '''
    return path.is_dir()

def create_path(path: Path) -> None:
    '''
    Creates the path 
    '''
    try:
        if not path.is_dir():
            path.mkdir(parents = True, exist_ok = True)     
    except Exception as e:
        print(e)

def verify_config(filepath: Path) -> Path:
    '''
    Find the config file in the current working directory
    '''
    if  filepath.exists():
        return filepath
    else:
        return None

def calculate_path(yt: Union[Channel, Playlist, YouTube]) -> Path:
    '''
    Calculates the filepath for the given object.
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
              | -- single name
                        | -- videos
                        | -- captions
                        | -- audio
                        | -- thumbnails
    '''
    path_dict = {Channel: "channels", Playlist: "playlists", YouTube: "singles"}    # Dict to sort from object to path
    print("Type = ", type(yt))
    path = Path(path_dict[type(yt)])            # The object type will inform us where to sort it
    print("Path = ", path)
    pathname = path/Path(parser.get_name(yt))   # Add the channel/playlist/single's name to the path
    # Resolve collision, need to add some handling here in case we want to overwrite
    return "str(pathname)"

# TODO
def resolve_collision(yt: YouTube, filename: Path) -> Path:
    '''
    Changes the filename if one already exists with the same name
    '''
    return ''

# This can either get the filename from the pytube stream object, or it can generate
# It itself from the title
# RESOLUTION: For now we will just use the title until this breaks things
def calculate_filename(yt: YouTube) -> str:
    '''
    Determines the filename from the youtube object
        Must handle collision
    '''
    try:
        filename = yt.title
        # filename = resolve_collision()
        return filename
    except Exception as e:
        return None

def calculate_path(yt: Union[Channel, Playlist, YouTube]) -> str:
    '''
    Determines the output path for the given pytube object
    '''

