
'''
This module handles all of the downloading to disk, and parses whatever 
filters were passed down from the config 
'''
from pytube import YouTube
from typing import Optional
import logging
from pathlib import Path

defaults = {
    "video_extension": ".mp4",
    "audio_extension": ".mp3",
    "resolution": "best"
    }


def download_single(yt: YouTube, **kwargs):
    '''
    Takes a single YouTube object and handles the downloading based on configs
    '''
    # If video, download_video()
    # If caption, download_captions()
    # If audio, download_audio()
    # If thumbnail, download_thumbnail()


def download_video( 
    url: str, 
    filename: Optional[str] = None, 
    output_path : Optional[str] = "", 
    **kwargs
) -> str:
    '''
    Download a single video
    '''
    yt = YouTube(url)
    title = yt.title
    author = yt.author
    stream = yt.streams.get_highest_resolution()
    # Must have the root in the path
    output_path += "videos/"
    if not filename:
        filename = stream.default_filename
    print(f'Saving {title} to {output_path + filename}')
    
    # Download the video
    logging.info("Downloading %s to %s", url, output_path)
    try:
        stream.download(output_path, filename)
    except FileNotFoundError:   # If the directory doesn't exist, create it
        logging.info(f"Creating directory {output_path}")
        os.makedirs(output_path, exist_ok=True)
    filepath = output_path + filename
    return filepath # Return the filepath of the downloaded video

def download_captions(
    url: str,
    filename: Optional[str] = None,
    output_path: Optional[str] = "",
    **kwargs
    ) -> str:
    '''
    Download selected captions from a video
    '''
    filepath = ""
    output_path += "videos/"
    return filepath