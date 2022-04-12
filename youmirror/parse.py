# This file will parse information from YouTube objects
from pytube import YouTube
from typing import cls, Dict
import logging
types = {"channel", "playlist", "video"}

def check_type(url: str) -> str:
    if "/user/" in url:
        return "channel"
    pass

def get_metadata(yt: YouTube) -> Dict:
    metadata = {}
    metadata["title"] = yt.title
    metadata["author"] = yt.author
    return metadata

def is_available(yt: YouTube) -> bool:
    try:
        yt.check_availability()
    except Exception as e:
        logging.exception(f"Video is not available due to {e}")   # Need to report the url or the title if we can
    return True