'''
This module parses youtube urls, wraps them in pytube objects and 
pulls information from pytube objects
---
'''
from pytube import YouTube, Channel, Playlist, extract
from typing import Union
import logging

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

def link_id(url: str, yt_string = None) -> str:
    '''
    Uses pytube's extract module to get the id from a url (more lightweight than creating an object)
    '''
    yt_string_to_func = {"channel": extract.channel_name, "playlist": extract.playlist_id, "single": extract.video_id}  # Translation dict from yt type to function

    if not yt_string:                   # Calculate the yt_string if not passed
        yt_string = link_type(url)
    func = yt_string_to_func[yt_string] # Extract the proper id from the url
    return func(url)
    
def yt_to_type_string(yt: Union[Channel, Playlist, YouTube]) -> str:
    '''
    Gets the type of the given pytube object and returns a string
    '''
    yt_type_to_string = {Channel: "channel", Playlist: "playlist", YouTube: "single"}    # Translation dict for convenience
    yt_type = type(yt)                      # Get type of pytube object
    if yt_type in yt_type_to_string:        # If it is a valid type
        return yt_type_to_string[yt_type]   # Return the translated string
    else:
        logging.error(f'Object {yt_type} is not a valid yt_type')


def get_metadata(yt: Union[Channel, Playlist, YouTube]) -> dict:
    '''
    Returns the metadata of a given pytube object as a dict
    '''
    meta = dict()
    meta["name"] = get_name(yt)             # Get the name
    meta["url"] = get_url(yt)
    if type(yt) in [Channel, Playlist]:     # Check if we have a channel or playlist
        children = get_children(yt)         # This will use pytube to get video_urls
        children_ids = set([link_id(child, "single") for child in children])    # We want the ids (not urls) for databasing purposes
        meta["children"] = children_ids     # Add the children ids to the metadata
        meta["available"] = True            # We will add a check later to determine this

    elif isinstance(yt, YouTube):
        meta["available"] = is_available(yt)    # Individual videos can be checked if they are available
    return meta

def is_available(yt: YouTube) -> bool:
    try:
        yt.check_availability()
    except Exception as e:
        logging.exception(f"Video {yt.title} is not available due to {e}")   # Need to report the url or the title if we can
    return True

def new_pytube(url: str) -> Union[YouTube, Channel, Playlist]:
    '''
    This replaces get_pytube and returns a new pytube object from url
    '''
    objects = {"channel": Channel, "playlist": Playlist, "single": YouTube}
    url_type = link_type(url)                       # Returns what type of link it is (as string)
    try:
        object = wrap_url(url, objects[url_type])   # Wrap the url in the proper pytube object
        return object
    except Exception as e:
        logging.exception(f"Failed to parse Youtube link due to {e}")
        return None         # This indicates something went wrong, but we will handle it above

def wrap_url(url: str, object: Union[YouTube, Channel, Playlist]) -> Union[YouTube, Channel, Playlist]:
    '''
    Wraps the url in the proper pytube object
    '''
    return object(url)

def get_id(yt: Union[YouTube, Channel, Playlist]) -> str:
    """
    Returns the id of the pytube object
    """
    type_to_id = {YouTube: "video_id", Channel: "channel_uri", Playlist: "playlist_id"}    # Translation dict from type to attribute
    t = type(yt)
    if t in type_to_id:
        return getattr(yt, type_to_id[t])
    else:
        logging.error(f"Failed to get id for {yt}")
        return None

def get_name(yt: Union[YouTube, Channel, Playlist]) -> str:
    """
    Returns the name of the pytube object
    """
    type_to_name = {YouTube: "title", Channel: "channel_name", Playlist: "title"}    # Translation dict from type to attribute
    t = type(yt)                         # Get the type of the object
    if t in type_to_name:                # If it is a valid type
        return getattr(yt, type_to_name[t])   # Return the attribute
    else:
        logging.error(f"Failed to get name for {yt}")
        return None

def get_url(yt: Union[YouTube, Channel, Playlist]) -> str:
    """
    Returns the url of the pytube object
    """
    type_to_url = {YouTube: "watch_url", Channel: "vanity_url", Playlist: "playlist_url"}    # Translation dict from type to property
    t = type(yt)                         # Get the type of the object
    if t in type_to_url:                # If it is a valid type
        return getattr(yt, type_to_url[t])   # Return the attribute
    else:
        logging.error(f"Failed to get url for {yt}")
        return None

def get_children(yt: Union[Channel, Playlist]) -> list[str]:
    '''
    Takes either a Channel or Playlist object and returns its video links as a list of strings
    '''
    try:
        logging.debug(f"Getting children for {get_name(yt)}")
        children = [url for url in yt.video_urls]   # Maybe we can async get this in the future?
        return children
    except Exception as e:
        logging.exception(f"Failed to get children for {get_name(yt)} due to {e}")
        return None