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

defaults = {                # These are the default global configs if not specified
    "filetree": "tall",     # This sets the filetree type ----- currently not implemented
    "resolution": "highest",   # What type of video resolution to download
    "dry_run": False,       # Dry run means don't download automatically
    "dl_video": True,       # Whether to download video
    "dl_captions": True,   # Whether to download captions
    "dl_audio": False,      # Whether to download audio
    "dl_thumbnail": False,  # Whether to download the thumbnail
    "captions": ["en", "a.en"]  # Which caption types to check for
}

config_file = "youmirror.toml"                                      # This is the name for the config file to be used
valid_options = {"youmirror", "channel", "playlist", "single"}   # These are the valid global options
valid_yt = {"channel", "playlist", "single"}                        # Valid youtube types for the config

def set_options(option: str, config: dict, options: dict) -> dict:
    '''
    Sets the options for the given config parameter from a dictionary
    '''
    # TODO this doesn't feel right. I think I should go back to just setting it directly
    if option in valid_options:                 # If the option is valid
        for key in options.keys():              # For each key in the options
            config[option][key] = options[key]  # Set the option to the value
        return config                           # Return the config
    else:
        logging.info(f"Invalid option {option}")
        return None
    
def get_options(option: str, config: dict) -> dict:
    '''
    Gets the options for the given config parameter
    '''
    if option in valid_options:
        return config[option]
    else:
        logging.info(f"Invalid id {option}")
        return None
    
# TODO
# This can be refactored to utilize one of the other functions but to be totally honest I'm not sure how to do it
# channel, channel_id, config, dict of settings
def set_yt(yt: str, id: str, config: dict,  options: dict) -> dict:
    '''
    Sets the options for the given id
    '''
    if yt in valid_yt:
        config[yt][id] = options
        return config
    else:
        logging.error(f"Invalid youtube type {yt}")
        return None

def get_yt(yt: str, id: str, config: dict) -> dict:
    '''
    Sets the options for the given id
    '''
    if yt in valid_yt and yt_exists(yt, id, config):    # If we are checking
        return config[yt][id]
    else:
        logging.error(f"Invalid youtube type {yt} or id {id} does not exists")
        return None

def yt_exists(yt: str, id: str, config: dict) -> bool:
    '''
    Checks if the url exists
    '''
    if yt in valid_yt:
        return id in config[yt]
    else:
        logging.error(f"Invalid youtube type {yt}")
        return False

# TODO if yt doesn't exists, set it
def add_yt(yt: str, id: str, config: dict, options: dict) -> dict:
    '''
    Adds the yt id to the config if it doesn't exist
    '''
    if not yt_exists(yt, id, config):
        set_yt(yt, id, config, options)
        return options
    else:
        logging.error(f"id {id} already exists")
        return None

def remove_yt(yt: str, id: str, config: dict) -> dict:
    '''
    Removes yt id from the config if it exists
    '''
    if yt_exists(yt, id, config):
        del config[yt][id]
        return config
    else:
        logging.error(f"Invalid youtube type {yt}")
    return

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
            d = {"name": name, "created_at": created_at}    # New options
            set_options("youmirror", template, d)           # Save the additional options            
            return save_config(config_path, template)       # Save the config
        else:
            logging.info(f'Config file {config_path} already exists')
            return None
    except Exception as e:
        logging.exception(f"Failed to create new config file due to {e}")


