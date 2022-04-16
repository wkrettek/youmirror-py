
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
    if file_type == "audio":
        stream = yt.streams.get_audio_only()
    else:
        stream = yt.streams.get_highest_resolution()
    return stream

def download_stream(stream: Stream, path: str, filename: str, options: dict) -> bool:
    '''
    Downloads to the given filepath and returns if a new file was downloaded or not
    '''
    filename = filename + ".mp4"
    stream.download(output_path=path, filename=filename) # Download to the appropriate path and name
    return True

def download_video(yt: YouTube, path: str, filename: str, options: dict) -> None:
    '''
    Gets the proper stream for video and downloads it
    '''
    try:
        stream = get_stream(yt, "video", options)     # Get stream with applied filters
        download_stream(stream, path, filename, options)
    except Exception as e:
        logging.exception(f'Could not download video at {path + filename}')

def download_caption(yt: YouTube, path: str, filename: str, options: dict) -> str:
    '''
    Gets the captions from the video and downloads them
    # TODO This implements a uses a fix that is not in pytube right now so it is in my wkrettek repo
    Probably should just implement it in this library until pytube is updated
    '''
    # TODO handle for different languages
    captions = yt.caption_tracks
    for c in captions:
        c.download(output_path=path, title=filename+str(c.__repr__()))
    return filename

def download_audio(yt: YouTube, path: str, filename: str, options: dict) -> str:
    '''
    Gets the audio from a video and downloads it
    '''
    options["dl_audio"] = True
    try:
        stream = get_stream(yt, "audio", options)
        download_stream(stream, path, filename, options)
    except Exception as e:
        logging.exception(f'Could not download video {filename}')


def download_thumbnail(yt: YouTube, path: str, filename: str, options: dict) -> str:
    '''
    Gets the thumbnail from the video and downloads it
    '''
    try:
        url = yt.thumbnail_url  # For now, pytube can only get the url for a thumbnail
        filepath = Path(path)/Path(filename)            # Add the path and filename
        filename: Path = filepath.with_suffix(".jpg")   # Add the extension for the thumbnail
        filename.touch()                                # Create the file if it doesn't already exist
        urlretrieve(url, filename=filename)             # Download to filename
    except Exception as e:
        logging.exception(f'Could not download thumbnail at {filename}')
    # TODO implement a way to download the url, probably copy however pytube manages to do it without dependencies

def download_single(yt: YouTube, filepath: str, options: dict) -> None:
    '''
    Takes a single YouTube object and handles the downloading based on configs
    '''
    extension_to_file_type = {  # Translation from file extension to file type
        ".mp4":"video", ".mp3": "audio", 
        ".srt": "caption", ".jpg": "thumbnail"}

    file_type_to_do = {         # Translation from file type to func
        "video": download_video, 
        "audio": download_audio, 
        "caption": download_caption, 
        "thumbnail": download_thumbnail}

    filepath = Path(filepath)       # Convert to Path
    path = filepath.parent          # Get the path
    filename = filepath.stem        # Get the filename

    print(f"Downloading {filepath}")

    extension = Path(filepath).suffix   # Get the extension
    file_type = extension_to_file_type[extension]   # Convert to file type
    func = file_type_to_do[file_type]   # Figure out what to do
    func(yt, path, filename, options)         # Call the function