# This file will parse information from youtube urls and deal with pytube objects
from pytube import YouTube, Channel, Playlist
from typing import Union, List, Dict
import youmirror.helper as helper
import youmirror.configurer as configurer
import logging
import sys
types = {"channel", "playlist", "video"}

# In the future, this should be two functions, one that returns the type and one that checks if the link is valid. For now, it does both
def check_link(url: str) -> str:
    '''
    Really rough way to narrow down a link before creating a pytube object
    '''
    channel_strings = {'/user/', '/channel/', '/c/'}        # Possible strings for a channel
    if any(string in url for string in channel_strings):    # For some reason youtube has really inconsistent urls, so here we are
        return "channel"
    elif "playlist?list" in url:
        return "playlist"
    elif "watch?v=" in url:
        return "single"
    else:
        logging.error(f"\'{url}\' is not a valid url")
        sys.exit()
        return None

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

def get_pytube(url: str, type: str) -> Union[YouTube, Channel, Playlist]:
    '''
    Returns the proper pytube object for the url
    '''
    objects = {"channel": Channel, "playlist": Playlist, "single": YouTube}
    try:
        object = wrap_url(url, objects[type])   # Wrap the url in the proper pytube object
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

def get_children(yt: Union[Channel, Playlist]) -> List[str]:
    '''
    Takes either a Channel or Playlist object and returns the video links inside it as a list of strings
    '''
    if isinstance(yt, Channel):
        logging.info(f"Getting children for {yt.vanity_url}")
        return [url for url in yt.video_urls]
    elif isinstance(yt, Playlist):
        return [url for url in yt.video_urls]
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


def get_keys(yt: Union[Channel, Playlist, YouTube]) -> Dict:
    '''
    Gets the keys that we want to put into the database and returns as a dictionary
    '''
    keys = dict()
    if isinstance(yt, Channel):
        keys["name"] = yt.channel_name
        keys["children"] = get_children(yt)
        keys["available"] = True            # We will add a check later to determine this
        keys["path"] = helper.calculate_path(yt)
        return keys
    elif isinstance(yt, Playlist):
        keys["name"] = yt.title
        keys["children"] = get_children(yt)
        keys["available"] = True            # We will add a check later to determine this
        keys["path"] = helper.calculate_path(yt)
        return keys
    elif isinstance(yt, YouTube):
        keys["name"] = yt.title
        keys["parent"] = None               # Singles will only get here if there is no parent
                                            # If there is a parent, we will add it later
        keys["available"] = is_available(yt)
        keys["path"] = helper.calculate_path(yt)
        keys["captions"] = configurer.get_captions()    # Get the captions we want to download for this video
        keys["filename"] = helper.calculate_filename()

        return keys
    else: 
        return None