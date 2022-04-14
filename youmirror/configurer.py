'''
This module manages the config
I decided on using toml over json because it's easier to read and edit.
Ideally this module will abstract the configuration management away from
the top-level class
-------
globals - Toplevel global options AKA YouMirror settings
yts     - YouTube specific options
ids     - YouTube specific ids

'''
import toml
import logging
from datetime import datetime
from pathlib import Path

config_file = "youmirror.toml"                                      # This is the name for the config file to be used
valid_options = {"youmirror", "channels", "playlists", "singles"}   # These are the valid global options
valid_yt = {"channels", "playlists", "singles"}                     # Valid youtube types for the config

def set_options(option: str, config: dict, options: dict) -> dict:
    '''
    Sets the options for the given config parameter
    '''

    if option in valid_options:
        config[option] = options
        return config
    else:
        logging.info("Invalid id {id}")
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
        return options
    else:
        logging.error("Invalid youtube type {yt}")
        return None

def get_yt(yt: str, id: str, config: dict) -> dict:
    '''
    Sets the options for the given id
    '''
    if yt in valid_yt and yt_exists(yt, id, config):    # If we are checking
        return config[yt][id]
    else:
        logging.error("Invalid youtube type {yt} or {id} does not exists")
        return None

def yt_exists(id: str, yt: str, config: dict) -> bool:
    '''
    Checks if the url exists
    '''
    if yt in valid_yt:
        return id in config[yt]

def load_config(config_path: str) -> dict:
    '''
    Loads the config file and returns as a dictionary
    '''
    try:
        return toml.load(open(config_path))
    except Exception as e:
        logging.exception(f"Could not parse given config file due to {e}")
        return None

def save_config(config_path: Path, config: dict) -> Path:
    '''
    Writes the config dictionary to the config file, return the path if successful
    '''
    try:
        if config_path.is_file():                      # Check if the file exists     
            toml_string = toml.dumps(config)           # Convert the config to a toml string
            print("New config: \n" + toml_string)      # Print the new config ----- Remove later
            config_path.open('w').write(toml_string)   # Write the toml string to the config file
        else:
            return None
    except Exception as e:
        logging.exception(f"Could not write config file due to {e}")
        return None

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
            logging.info('Config file {config_path} already exists')
            return None
    except Exception as e:
        logging.exception(f"Failed to create new config file due to {e}")
        return None

# TODO if yt doesn't exists, set it
def add_yt(yt: str, id: str, config: dict, options: dict) -> dict:
    '''
    Adds the yt id to the config
    '''
    if yt in valid_yt:
        config[yt][id] = options
        return options
    else:
        logging.error("Invalid youtube type {yt}")
        return None

# TODO if yt does exist, remove it
def remove_yt(yt: str, id: str, config: dict) -> None:
    '''
    Removes yt id from the config
    '''
    if yt in valid_yt:
        del config[yt][id]
    else:
        logging.error("Invalid youtube type {yt}")
    return

def add_item(id: str, specs: dict, config: dict) -> None:
    '''
    Adds the url to the config
    '''
    if specs["type"] == "channel":
        channels = config["channels"]
        channels[id] = specs  # Add the url to the config
        # TODO add options to the item
    elif specs["type"] == "playlist":
        playlists = config["playlists"]
        playlists[id] = specs  # Add the url to the config
    elif specs["type"] == "single":
        singles = config["singles"]
        singles[id] = specs
    return

def remove_item(id: str, config: dict) -> None:
    '''
    Removes the url from the config
    '''
    if id in config["channels"]:
        del config["channels"][id]
    elif id in config["playlists"]:
        del config["playlists"][id]
    elif id in config["singles"]:
        del config["singles"][id]
    return


