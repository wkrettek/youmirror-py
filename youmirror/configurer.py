'''
This module manages the config
I decided on using toml over json because it's easier to read and edit.
Ideally this module will abstract the configuration management away from
the top-level class
'''
import toml
import logging
from datetime import datetime
from pathlib import Path

config_file = "youmirror.toml"

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
            print("New config: \n" + toml_string)      # Print the new config
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
        from youmirror.template import template         # Import the template dictionary
        template["name"] = root                         # Set the name to the new mirror's root
        template["created"] = datetime.datetime.now().strftime('%Y-%m-%d') # Mark the creation date
        save_config(config_path, template)              # Save the config
    except Exception as e:
        logging.exception(f"Failed to create new config file due to {e}")
        return None

def id_exists(id: str, type: str, config: dict) -> bool:
    '''
    Checks if the url exists
    '''
    if type == "channel":
        return id in config["channels"]
    elif type == "playlist":
        return id in config["playlists"]
    elif type == "single":
        return id in config["singles"]
    return False

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

def get_captions(id: str) -> str:
    '''
    Returns what captions to download for the given id
    '''
    # Get the list from the config
    # Take the list and join with spaces
    # Return string
    return ''

def set_global_options(config: dict, options: dict) -> None:
    '''
    Sets the global options
    '''
    # TODO
    return


