
'''
This module handles all of the downloading to disk, and parses whatever 
filters were passed down from the config 

My first priority is finding the best matching resolution when the user specifies it. Then, the container (mp4/webm) has to match the audio codec so we can combine them. The absolute basic default is to download the highest resolution video and audio. If we download by resolution we can use stream.includes_audio_track to decide if we have to find a matching audio track.

I could maybe make other types of downloads available. I think a possible one is like a metadata and another one is like the js. Could be useful

'''
from pytube import YouTube, StreamQuery, Stream, Caption, request
import pytube.request as request
import logging
from pathlib import Path
import subprocess
from urllib.request import urlretrieve  # Using this to download thumbnails

file_types = {"video", "caption", "audio", "thumbnail"} # TODO download js and raw html?
# Order resolutions from highest to lowest in a list
resolutions = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"] # Stored as a list because order is important
sub_types = ["mp4", "webm"]    # Prefer mp4 over webm

def get_stream(yt: YouTube, file_type: str, options: dict) -> Stream:
    '''
    Applies all the filters and gets a stream object
    '''
    subtype = "mp4" # This is the subtype we're gonna go with
    if "resolution" in options: resolution = options["resolution"]  # Get the resolution from the options
    if file_type == "audio":
        stream = yt.streams.filter(only_audio=True, subtype=subtype).order_by("abr").desc()
    else:
        stream = yt.streams.get_highest_resolution()
    return stream

def get_video_stream(yt: YouTube, options: dict) -> Stream:
    '''
    Gets the video stream from the video
    '''
    if options["has_ffmpeg"]:             # If resolution is specified
        resolution = options["resolution"]  # Get the resolution from the options
    else:
        return yt.streams.filter(progressive=True, subtype="mp4").order_by("resolution").last()  # Else, get the highest res progressive stream (usually 720p)
    stream = None       # Initialize the stream
    find_res = iter(resolutions[resolutions.index(resolution):]) # Iterate through the resolutions
    while not stream:   # Until we find a good one
        streams = yt.streams.filter(subtype="mp4", resolution=resolution) # Filter streams by resolution
        stream = next(iter(streams), None)  # Get the first stream or none if there is no stream
        resolution = next(find_res) # Get the next resolution
    return stream

def get_audio_stream(yt: YouTube, options: dict) -> Stream:
    '''
    Gets the audio stream from the video
    '''
    return yt.streams.get_audio_only()  # This returns the highest bitrate audio stream by default (mp4)

def combine_video_audio(video_file: str, audio_file: str) -> str:
    '''
    Combines the video and audio files
    '''
    temp = Path(f'{video_file}.temp')   # Create temp file
    temp.touch()                        # Create the file   
    Path(video_file).rename(temp)       # Rename the video file to the temp file
    temp = str(temp)                    # Convert to string
    subprocess.run(["ffmpeg", "-y", "-i", f"{temp}", "-i", f"{audio_file}", "-c:v", "copy", "-c:a", "copy", f"{video_file}"], capture_output=True)               # Use ffmpeg to combine the video and audio
    Path(audio_file).unlink()     # Delete the temp audio file
    Path(temp).unlink()           # Delete the temp video file
    return video_file

def calculate_video_filesize(yt: YouTube, options: dict) -> int:
    '''
    Calculates the size of a video file
    '''
    video_stream = get_video_stream(yt, options)    # Get the video stream
    filesize = video_stream.filesize                # Add the filesize
    if not video_stream.includes_audio_track:       # If there is no audio
        filesize += calculate_audio_filesize(yt, options)   # Add the audio filesize
    return filesize
    

def calculate_audio_filesize(yt: YouTube, options: dict) -> int:
    '''
    Calculates the size of an audio file
    '''
    return get_audio_stream(yt, options).filesize


def calculate_caption_filesize(yt: YouTube, options: dict) -> int:
    '''
    Calculates the size of a caption file
    '''
    return 0    # Just assume 0 until we get a good option

def calculate_thumbnail_filesize(yt: YouTube, options: dict):
    '''
    Calculates the size of a thumbnail file
    '''
    url = yt.thumbnail_url          # Get the thumbnail url
    filesize = request.seq_filesize(url)    # Use pytube's request module to get the filesize
    return filesize


def calculate_filesize(yt: YouTube, file_type: str, options: dict) -> int:
    '''
    Gets the size of the file type 
    '''
    file_type_to_func = {"video": calculate_video_filesize, "audio": calculate_audio_filesize, "caption": calculate_caption_filesize, "thumbnail": calculate_thumbnail_filesize}
    func = file_type_to_func[file_type]
    filesize = func(yt, options)
    return filesize

def download_stream(stream: Stream, path: str, filename: str, options: dict) -> bool:
    '''
    Downloads to the given filepath and returns if a new file was downloaded or not
    '''
    stream.download(output_path=path, filename=filename) # Download to the appropriate path and name
    return True

def download_video(yt: YouTube, path: str, filename: str, options: dict) -> str:
    '''
    Gets the proper stream for video and downloads it
    '''
    try:

        video_stream = get_video_stream(yt, options)                # Get the video stream
        download_stream(video_stream, path, filename, options)      # Download the video stream
        if not video_stream.includes_audio_track:                   # If no audio track
            filepath = str(Path(path)/Path(filename))             # Get the filepath
            audio_stream = get_audio_stream(yt, options)            # Get the audio stream
            download_stream(audio_stream, path, "temp_audio.mp4", options)  # Download the audio stream
            audio_filepath = str(Path(path)/Path("temp_audio.mp4")) # Get the audio filepath
            combine_video_audio(filepath, audio_filepath) # Combine the video and audio
    except Exception as e:
        logging.exception(f'Could not download video at {str(path) + filename}')

def download_caption(yt: YouTube, path: str, filename: str, options: dict) -> str:
    '''
    Gets the captions from the video and downloads them
    # TODO This implements a uses a fix that is not in pytube right now so it is in my wkrettek repo
    Probably should just implement it in this library until pytube is updated
    '''
    # TODO handle for different languages
    caption_type = options["caption_type"]  # Language was injected from above
    captions = yt.captions            # Get the captions
    for caption in captions:         # Iterate through the captions
        if caption.code == caption_type:    # If the caption is the language we want
            caption.download(output_path=path, title=filename) # Download the caption
            return filename
    print("Could not find caption for language: " + caption_type)
    return None

def download_audio(yt: YouTube, path: str, filename: str, options: dict) -> str:
    '''
    Gets the audio from a video and downloads it
    -----
    Stream looks like yt.streams.filter(only_audio=True, subtype="mp4").desc()
    Audio files are coming out too long, so we want to trim it to the reported length if it is longer
    '''
    try:
        length = yt.length                                  # Get the length of the video
        stream = get_audio_stream(yt, options)           # Get the audio stream
        stream.download(output_path=path, filename=filename)    # Download the audio stream
        if options["has_ffmpeg"]:                           # TODO If they have ffmpeg, trim the audio
            pass
            # subprocess.run(["ffmpeg", "-y", "-i", f"{path}{filename}", "-ss", "00:00:00", "-t", f"{length}", f"{path}{filename}"])
        return filename
    except Exception as e:
        logging.exception(f'Could not download video {filename}')
        return None
    return None


def download_thumbnail(yt: YouTube, path: str, filename: str, options: dict) -> str:
    '''
    Gets the thumbnail from the video and downloads it
    '''
    try:
        path = Path(path)                       # Wrap the path
        path.mkdir(parents=True, exist_ok=True) # Create the directory if it doesn't exist
        filepath = path/Path(filename)  # Build the filepath
        filepath.touch()                # Create the file
        url = yt.thumbnail_url          # For now, pytube can only get the url for a thumbnail
        urlretrieve(url, filepath)      # Download the thumbnail
        return filename
    except Exception as e:
        logging.exception(f'Could not download thumbnail at {filepath}')
        return None

def download_single(yt: YouTube, file_type: str, filepath: str, options: dict) -> None:
    '''
    Takes a single YouTube object and handles the downloading based on configs
    '''

    file_type_to_do = {         # Translation from file type to func
        "video": download_video, 
        "audio": download_audio, 
        "caption": download_caption, 
        "thumbnail": download_thumbnail}

    print(f"Downloading {filepath}")

    path = str(Path(filepath).parent)    # Extract the path
    filename = str(Path(filepath).name)  # Extract the filename
    func = file_type_to_do[file_type]    # Figure out what to do
    return func(yt, path, filename, options)    # Call the function