'''
This module parses youtube urls, wraps them in pytube objects and 
pulls information from pytube objects
'''
from pytube import YouTube, Channel, Playlist
from typing import Union, Callable, Any
import youmirror.helper as helper
import youmirror.configurer as configurer
import logging

yt_type_to_string = {Channel: "channel", Playlist: "playlist", YouTube: "single"}    # Translation dict for convenience

def link_type(url: str) -> str:
    '''
    Really rough way to narrow down a link before creating a pytube object
    '''
    channel_strings = {'/user/', '/channel/', '/c/'}        # Possible strings for a channel
    if any(string in url for string in channel_strings):    # For some reason youtube has really inconsistent urls, so here we are
        return "channel"
    elif "playlist?list" in url:                            # String to check for a playlist
        return "playlist"
    elif "watch?v=" in url:                                 # String to check for a video
        return "single"
    else:
        logging.error(f"\'{url}\' is not a valid url")
        return None
    
def yt_to_type_string(yt: Union[Channel, Playlist, YouTube]) -> str:
    '''
    Gets the type of the given pytube object and returns a string
    '''
    yt_type = type(yt)                      # Get type of pytube object
    if yt_type in yt_type_to_string:        # If it is a valid type
        return yt_type_to_string[yt_type]   # Return the translated string
    else:
        logging.error(f'Object {yt_type} is not a valid yt_type')


def get_metadata(yt: YouTube) -> dict:
    print(yt.metadata)
    metadata = {}
    metadata["title"] = yt.title
    metadata["author"] = yt.author
    return metadata

def is_available(yt: YouTube) -> bool:
    try:
        yt.check_availability()
    except Exception as e:
        logging.exception(f"Video {yt.title} is not available due to {e}")   # Need to report the url or the title if we can
    return True

def get_pytube(url: str) -> Union[YouTube, Channel, Playlist]:
    '''
    Returns the proper pytube object from a url
    '''
    objects = {"channel": Channel, "playlist": Playlist, "single": YouTube}
    url_type = link_type(url)                       # Returns what type of link it is
    try:
        object = wrap_url(url, objects[url_type])   # Wrap the url in the proper pytube object
        return object
    except Exception as e:
        logging.exception(f"Failed to parse Youtube link due to {e}")
        return None         # This indicates something went wrong, but we will handle it above

def resolve_pytube(yt: Union[Channel, Playlist, YouTube], do: dict[Any: Callable]):
    '''
    Returns the proper function to do for the pytube object
    '''
    return do[yt]

def wrap_url(url: str, object: Union[YouTube, Channel, Playlist]) -> Union[YouTube, Channel, Playlist]:
    '''
    Wraps the url in the proper pytube object
    '''
    return object(url)

def get_id(yt: Union[YouTube, Channel, Playlist]) -> str:
    """
    Returns the id of the pytube object
    """
    # funcs = {YouTube: get_id_from_video, Channel: get_id_from_channel, Playlist: get_id_from_playlist}
    # pytype = type(yt)
    # func = funcs[pytype]
    # return func(yt)
    if isinstance(yt, YouTube):
        return yt.video_id
    elif isinstance(yt, Channel):
        return yt.channel_uri
    elif isinstance(yt, Playlist):
        return yt.playlist_id
    else:
        logging.error(f"Failed to get id for {yt}")
        return None

def get_name(yt: Union[YouTube, Channel, Playlist]) -> str:
    """
    Returns the name of the pytube object
    """
    if isinstance(yt, YouTube):
        return yt.title
    elif isinstance(yt, Channel):
        return yt.channel_name
    elif isinstance(yt, Playlist):
        return yt.title
    else:
        logging.error(f"Failed to get name for {yt}")
        return None

def get_url(yt: Union[YouTube, Channel, Playlist]) -> str:
    """
    Returns the url of the pytube object
    """
    if isinstance(yt, YouTube):
        return yt.watch_url
    elif isinstance(yt, Channel):
        return yt.vanity_url
    elif isinstance(yt, Playlist):
        return yt.playlist_url
    else:
        logging.error(f"Failed to get url for {yt}")
        return None

def get_children(yt: Union[Channel, Playlist]) -> list[str]:
    '''
    Takes either a Channel or Playlist object and returns its video links as a list of strings
    '''
    if isinstance(yt, Channel):
        logging.debug(f"Getting children for {yt.vanity_url}")
        children = [url for url in yt.video_urls]  # Will need to simplify this later on 
        return children
    elif isinstance(yt, Playlist):
        logging.debug(f"Getting children for {yt.title}")
        children = [url for url in yt.video_urls]  # Will definitely wrap this in a function later on
        return children
    else: 
        return None

def is_available(yt: YouTube) -> bool:
    '''
    Returns whether a given pytube object is available
    '''
    try:
        yt.check_availability()
        return True
    except Exception as e:
        return False


def get_keys(yt: Union[Channel, Playlist, YouTube], keys: dict, options: str, filetree: dict) -> dict:
    '''
    Gets the keys that we want to put into the database and returns as a dictionary
            Channels
                id
                name
                children
                available
                paths
            Playlists
                id
                name
                children
                available
                path
            Singles
                id
                name
                parent
                available
                path
                captions
    You can pass in a dict if you want to inject some values from above
    This is going to be a heavy function that calls from a lot of places. It's calculating a lot of things
    '''
    dl = options["dl_video"]
    if isinstance(yt, Channel):
        keys["name"] = yt.channel_name
        children = get_children(yt)
        children_ids = [get_id(get_pytube(child)) for child in children]
        keys["children"] = children_ids
        keys["available"] = True            # We will add a check later to determine this
        keys["path"] = helper.calculate_path(yt)
        return keys
    elif isinstance(yt, Playlist):
        keys["name"] = yt.title
        children = get_children(yt)
        children_ids = [get_id(get_pytube(child)) for child in children]
        keys["children"] = children_ids
        keys["available"] = True            # We will add a check later to determine this
        keys["path"] = helper.calculate_path(yt)
        return keys
    elif isinstance(yt, YouTube):
        keys["name"] = yt.title
        # keys["parent"] = if "parent" in keys               # Singles will only get here if there is no parent
                                            # If there is a parent, we will add it later
        keys["available"] = is_available(yt)
        keys["path"] = 
        keys["files"] = helper.calculate_filepaths(yt)

        return keys
    else: 
        return None