# This module manages the config

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