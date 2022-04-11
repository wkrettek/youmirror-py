from typing import (
    Optional
)
import logging
import sqlite3
import ujson
from pytube import YouTube
import os
from pathlib import Path

# Create FileTree Class
class FileTree:

    def __init__(self, root : str = "./videos") -> None:
        self.root = "./videos/"
        self.logger = logging.getLogger(__name__)
        # self.db = sqlite3.connect(self.root + 'youmirror.db')

    def from_json(self, json_file: str) -> None:
        '''
        Load a json file
        '''
        json = ujson.load(open(json_file))
        self.root = json['root']

    def download_single(
        self, 
        url: str, 
        filename: Optional[str] = None, 
        output_path : Optional[str] = "", 
        is_channel: bool = False, 
        is_playlist : bool = False,
        playlist_title: str = ""
    ) -> None:
        '''
        Download a single video
        '''
        yt = YouTube(url)
        title = yt.title
        author = yt.author
        if not url:
            self.logger.error("No URL provided")
            return
        if not filename:
            filename = title + '.mp4'

        output_path += self.root    # Must have the root in the path
        if is_channel:              # Include author if the channel called us
            output_path += author 
        elif is_playlist:           # Include playlist title if the playlist called us
            output_path += playlist_title
        else:                       # Otherwise it's a single
            output_path += "singles/"
        
        # Download the video
        logging.info("Downloading %s to %s", url, output_path)
        try:
            yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(output_path=output_path, filename=filename)
        except FileNotFoundError:   # If the directory doesn't exist, create it
            logging.info(f"Creating directory {output_path}")
            os.makedirs(output_path, exist_ok=True)

    
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

# I'd like to make download_single robust and have the other two call on it I think
# Database name should be youmirror.db
# | -- root
#       | -- channels
#               | -- channel name
#                       | -- videos
#                       | -- captions
#                       | -- audio
#       | -- playlists
#              | -- playlist name
#                       | -- videos
#                       | -- captions
#                       | -- audio
#       | -- singles   
#              | -- videos
#              | -- captions
#              | -- audio
#
#