
'''
This module handles all of the downloading to disk, and parses whatever 
filters were passed down from the config 
'''
from pytube import YouTube, StreamQuery, Stream, Caption
import logging
from pathlib import Path
from urllib.request import urlretrieve  # Using this to download thumbnails

file_types = {"video", "caption", "audio", "thumbnail"}

def get_stream(yt: YouTube, file_type: str, options: dict) -> Stream:
    '''
    Applies all the filters and gets a stream object
    # TODO this implements a fix that is not in pytube right now so it is in my wkrettek repo,
    Need to implement myself until pytube is updated
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
    # TODO This implements a uses a fix that is not in pytube right now so it is in my wkrettek repo
    Probably should just implement it in this library until pytube is updated
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
    urlretrieve(url, filename=filepath)
    # TODO implement a way to download the url, probably copy however pytube manages to do it without dependencies

def download_single(yt: YouTube, filepath: str, options: dict):
    '''
    Takes a single YouTube object and handles the downloading based on configs
    '''
    extension_to_file_type = {
        "mp4":"video", "mp3": "audio", 
        "srt": "caption", ".jpg": "thumbnail"
        }

    file_type_to_do = { # Translation from file type to func
        "video": download_video, 
        "audio": download_audio, 
        "caption": download_caption, 
        "thumbnail": download_thumbail
    }
    extension = Path(filepath).suffix   # Get the extension
    file_type = extension_to_file_type[extension]   # Convert to file type
    func = file_type_to_do[file_type]   # Figure out what to do
    func(yt, filepath, options)         # Call the function