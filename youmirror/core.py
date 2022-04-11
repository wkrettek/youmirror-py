from typing import (
    Optional
)
import logging
import sqlite3
import ujson
from pytube import YouTube
import os
from pathlib import Path

# Create YouMirror Class
class YouMirror:

    def __init__(
        self,
        root : str = "./youmirror",
        ) -> None:
        self.logger = logging.getLogger(__name__)
        self.dbpath = self.root + 'youmirror.db'
        self.channels = {}
        self.playlists = []
        self.singles = []
        # self.db = sqlite3.connect(self.root + 'youmirror.db')

    def from_json(self, json_file: str) -> None:
        '''
        Load a json file
        '''
        json = ujson.load(open(json_file))
        self.root = json['root']

    def sync():
        '''
        Syncs the file tree and database against the config file
        '''
        # Check if the database exists
            # If no database, create a new one
        # Look through channels
            # For each video in channel
                # Compare against database
                    # If file does not exist
                        # Mark video for download
        # Look through playlists
            # For each video in playlist
                # Compare against database
        # Look through singles
            # Compare against database
        
        pass

    def check():
        '''
        
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