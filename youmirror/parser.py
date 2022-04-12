# This file will parse information from YouTube objects
from pytube import YouTube
from typing import Dict
import logging
types = {"channel", "playlist", "video"}

def link_type(url: str) -> str:
    if "/user/" in url or "/channel/" in url or '/c/' in url:   # For some reason youtube has really inconsistent urls, so here we are
        return "channel"
    elif "playlist?list" in url:
        return "playlist"
    elif "watch?v=" in url:
        return "video"
    else:
        return "unknown"
    pass

def get_metadata(yt: YouTube) -> Dict:
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