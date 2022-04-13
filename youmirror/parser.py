# This file will parse information from youtube urls
from pytube import YouTube
from typing import Dict
import logging
import sys
types = {"channel", "playlist", "video"}

# In the future, this should be two functions, one that returns the type and one that checks if the link is valid. For now, it does both
def check_link(url: str) -> str:
    if "/user/" in url or "/channel/" in url or '/c/' in url:   # For some reason youtube has really inconsistent urls, so here we are
        return "channel"
    elif "playlist?list" in url:
        return "playlist"
    elif "watch?v=" in url:
        return "single"
    else:
        logging.error(f"\'{url}\' is not a valid url")
        sys.exit()
        return None

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