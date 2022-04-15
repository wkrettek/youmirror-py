
'''
This module handles all of the downloading to disk, and parses whatever 
filters were passed down from the config 
'''
from pytube import YouTube, StreamQuery, Stream, CaptionQuery, Caption
from typing import Optional
import logging
from pathlib import Path

file_types = {"video", "caption", "audio", "thumbnail"}

def get_stream(yt: YouTube, file_type: str, options: dict) -> Stream:
    '''
    Applies all the filters and gets a stream object
    '''
    only_audio = False
    if file_type == "audio":
        only_audio = True
    query : StreamQuery = yt.streams(only_audio=only_audio)
    stream = query.filter()
    return stream

def download_stream(stream: Stream, filepath: str, options: dict) -> bool:
    '''
    Downloads to the given filepath and returns if a new file was downloaded or not
    '''
    filepath = Path(filepath)       # Convert to Path
    output_path = filepath.parent   # Get the path
    suffix = filepath.suffix        # Get the suffix
    filename = filepath.stem        # Get the filename
    Stream.download(output_path=output_path, filename=filename) # Download to the appropriate path and name
    print(f'Output path = {output_path} and filename = {filename}, suffix = {suffix}')
    return True

def download_video(yt: YouTube, filepath: str, options: dict) -> None:
    '''
    Gets the proper stream for video and downloads it
    '''
    file_type = "video"
    try:
        stream = get_stream(yt, file_type, options)     # Get stream with applied filters
        download_stream(stream, filepath, options)
    except Exception as e:
        logging.exception(f'Could not download video at {filepath}')

def download_caption(yt: YouTube, filepath: str, options: dict) -> str:
    '''
    Gets the captions from the video and downloads them
    '''
    # TODO handle for different languages
    file_type = "caption"
    captions: Caption = yt.captions
    captions.download()
    return "true"

def download_audio(yt: YouTube, filepath: str, options: dict) -> str:
    '''
    Gets the audio from a video and downloads it
    '''
    file_type = "audio"
    try:
        stream = get_stream(yt, file_type, options)
        download_stream(stream, filepath, options)
    except Exception as e:
        logging.exception(f'Could not download video at {filepath}')


def download_thumbail(yt: YouTube, filepath: str, options: dict) -> str:
    '''
    Gets the thumbnail from the video and downloads it
    '''
    file_type = "thumbnail"
    url = yt.thumbnail_url  # For now, pytube can only get the url for a thumbnail

def download_single(yt: YouTube, filepath: str, options: dict):
    '''
    Takes a single YouTube object and handles the downloading based on configs
    '''
    # If video, download_video()
    # If caption, download_captions()
    # If audio, download_audio()
    # If thumbnail, download_thumbnail()

# def download_video( 
#     url: str, 
#     filename: Optional[str] = None, 
#     output_path : Optional[str] = "", 
#     **kwargs
# ) -> str:
#     '''
#     Download a single video
#     '''
#     yt = YouTube(url)
#     title = yt.title
#     author = yt.author
#     stream = yt.streams.get_highest_resolution()
#     # Must have the root in the path
#     output_path += "videos/"
#     if not filename:
#         filename = stream.default_filename
#     print(f'Saving {title} to {output_path + filename}')
    
#     # Download the video
#     logging.info("Downloading %s to %s", url, output_path)
#     try:
#         stream.download(output_path, filename)
#     except FileNotFoundError:   # If the directory doesn't exist, create it
#         logging.info(f"Creating directory {output_path}")
#         os.makedirs(output_path, exist_ok=True)
#     filepath = output_path + filename
#     return filepath # Return the filepath of the downloaded video