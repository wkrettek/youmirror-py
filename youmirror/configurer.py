'''
This module manages the config
I decided on using toml over json because it's easier to read and edit.
Ideally this module will abstract the configuration management away from
the top-level class
-------
options - Toplevel global options AKA YouMirror settings
yts     - Youtube ids and their settings
ids     - YouTube specific ids (keys)

'''
import toml
import logging
from datetime import datetime
from pathlib import Path
from copy import deepcopy

defaults = {                # These are the default global configs if not specified
    "dry_run": False,       # Dry run means don't download automatically
    "resolution": "720p",   # Default video resolution
    "locked":False,         # Make no changes to the item
    "dl_video": True,       # Whether to download video
    "dl_captions": False,   # Whether to download captions
    "dl_audio": False,      # Whether to download audio
    "dl_thumbnail": False,  # Whether to download the thumbnail
    "captions": ["en", "a.en"]  # Which caption types to check for
}

config_file = "youmirror.toml"                                      # This is the name for the config file to be used
valid_options = {"youmirror", "channel", "playlist", "single"}      # These are the valid global options
valid_yt = {"channel", "playlist", "single"}                        # Valid youtube types for the config


def get_globals(config: dict) -> dict:
    '''
    Gets the options for the given config parameter
    '''
    config = deepcopy(config)   # Copy the config
    settings = config["youmirror"]
    return settings

def set_globals(config: dict, settings: dict) -> dict:
    '''
    Sets the options for the given config parameter from a dictionary
    '''
    config = deepcopy(config)
    config["youmirror"] = settings
    return config

def get_section(section: str, config: dict):
    '''
    Returns the appropriate section thingy
    '''
    return deepcopy(config[section])

def get_urls(config: dict) -> list[str]:
    '''
    Gets all the urls in the config
    '''
    urls: list[str] = []
    for yt in valid_yt:
        ids = config[yt]
        for id in ids:
            url = config[yt][id]["url"]
            urls.append(url)
    return urls   


def yt_exists(yt_string: str, id: str, config: dict) -> bool:
    '''
    Returns whether the yt id exists in the config
    '''

    yt_section = config[yt_string]                  # Get the section "channel, playlist, single"
    return id in yt_section                         # return if the id is in there

def get_yt(yt_string: str, id: str, config: dict) -> dict:
    '''
    Gets the dictionary for the given 
    '''
    yt = config[yt_string][id]
    return yt

def set_yt(yt_string: str, id: str, config: dict, settings) -> None:
    '''
    Sets the yt in the config and returns it
    '''
    config = deepcopy(config)
    config[yt_string][id] = settings
    return config

def remove_yt(yt_string: str, id: str, config: dict) -> dict:
    '''
    Removes the id from the appropriate yt section and returns the new config
    '''
    try:
        config = deepcopy(config)       # Copy config for safety
        yt_section = config[yt_string]  # Get the section "channel", "playlist", "single"
        if id in yt_section:            # If it's there
            del config[yt_string][id]   # Delete it
        return config
    except Exception as e:
        logging.exception('Could not remove %s, %s from config due to %s', yt_string, id, e)


def load_config(config_path: str) -> dict:
    '''
    Loads the config file and returns as a dictionary
    '''
    try:
        if Path(config_path).is_file():
            config = toml.load(open(config_path))   # Dictionary from the config file
            return config
        else:
            return None
    except Exception as e:
        logging.exception(f"Could not load config file {config_path} due to {e}")

def save_config(config_path: Path, config: dict) -> Path:
    '''
    Writes the config dictionary to the config file, return the path if successful
    '''
    try:
        if config_path.is_file():                      # Check if the file exists     
            toml_string = toml.dumps(config)           # Convert the config to a toml string
            config_path.open('w').write(toml_string)   # Write the toml string to the config file
        else:
            logging.error(f"Config file {config_path} does not exist")
            return None
    except Exception as e:
        logging.exception(f"Could not write config file due to {e}")

def new_config(config_path: Path, root: str) -> Path:
    '''
    Creates a new config file from the template
    '''
    # Fill out the config file with a template
    try:
        if not config_path.is_file():                       # Only if there isn't one already
            config_path.open(mode = "w")                    # Create the file
            from youmirror.template import template         # Import the template dictionary
            name = root                                     # Set the name to the new mirror's root
            created_at = datetime.now().strftime('%Y-%m-%d')# Mark the creation date
            info = {"name": name, "created_at": created_at} # New info
            set_globals(template, info)                     # Save the additional info         
            return save_config(config_path, template)       # Save the config
        else:
            logging.info(f'Config file {config_path} already exists')
            return None
    except Exception as e:
        logging.exception(f"Failed to create new config file due to {e}")


