import youmirror.databaser as databaser
import youmirror.downloader as downloader
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
        root : str = "./YouMirror",
        ) -> None:
        self.root = root
        self.dbpath = self.root + 'youmirror.db'
        self.channels = list()
        self.playlists = list()
        self.singles = list()

    def from_json(self, json_file: str) -> None:
        '''
        Load a json file into the YouMirror object
        '''
        try:
            config = ujson.load(open(json_file))
        except Exception as e:
            logging.exception(f"Could not parse given config file due to {e}")
        self.root = config['root']
        # Keep track of the urls of all the different types of files
        # Load channels
        for channel in config["channels"]:
            self.channels.append(channel)
            print(channel)
        # Load playlists
        for playlist in config["playlists"]:
            self.playlists.append(playlist)
            print(playlist)
        # Load singles
        for single in config["singles"]:
            self.singles.append(single)
            print(single)

    # Needs a little work, the root directory string gets printed strangely
    def new(
        self,
        config_file: str
        ) -> None:
        '''
        Create a new config file from the template
        '''
        try:
            from youmirror.template import template
            open(config_file, "w+").write(ujson.dumps(template, indent=4))
        except Exception as e:
            print(f"Failed to create new config file due to {e}")

    def add(
        self,
        url: str,
        download: bool
        ) -> None:
        '''
        Adds the following url to the mirror and downloads the video(s)
        '''
        pass

    def remove(
        self,
        url: str
        ) -> None:
        """
        Removes the following url from the mirror and deletes the video(s)
        """

    
    def sync(
        self,
        config_file: str
        ) -> None:
        '''
        Syncs the mirror against the config file
        '''
        # Check if the database exists
            # If no database, create a new one
        conn = databaser.connect_db(self.dbpath)
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

    def check(
        self
        ) -> None:
        '''
        Verify's which videos in the mirror are still available
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