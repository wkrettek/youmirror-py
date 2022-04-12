from pytube import YouTube
from typing import Optional
import logging
import os


def download_video( 
    url: str, 
    filename: Optional[str] = None, 
    output_path : Optional[str] = "", 
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
    ) -> str:
    '''
    Download selected captions from a video
    '''
    filepath = ""
    output_path += "videos/"
    return filepath


def download_channel(self, url: str, filename: Optional[str]) -> None:
    '''
    Download all videos from a channel
    '''
    prefix = self.root + "channels/" + YouTube(url).channel_id
    # self.download_single(url=url, filename=filename, filename_prefix=)
    pass

def download_playlist(self) -> None:
    '''
    Download all videos from a playlist
    '''
    pass