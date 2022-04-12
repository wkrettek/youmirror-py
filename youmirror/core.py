import youmirror.parser as parser
import youmirror.downloader as downloader
from typing import (
    Optional
)
import logging
import sqlite3
from urllib import parse
from sqlitedict import SqliteDict
import ujson
from pytube import YouTube, Channel, Playlist
from pathlib import Path
from tqdm import tqdm
import symbol
import os

# This is the main class for maintaining a youmirror
class YouMirror:

    def __init__(
        self,
        root : str = "./YouMirror/",
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
        self.dbpath = self.root + 'youmirror.db'
        # Keep track of the urls of all the different types of files
        # Load channels
        for channel in config["channels"]:
            self.channels.append(channel)
        # Load playlists
        for playlist in config["playlists"]:
            self.playlists.append(playlist)
        # Load singles
        for single in config["singles"]:
            self.singles.append(single)

    # Needs a little work, the root directory string gets printed strangely
    def new(
        self,
        root : str = "./YouMirror/",
        config_file: str = 'youmirror.json'
        ) -> None:
        '''
        Create a new config file from the template
        '''
        if Path(root + config_file).exists():
            print("Config file already exists")
            return
        if not Path(root).exists():
            os.mkdir(root)
        try:
            from youmirror.template import template
            open(root + config_file, "w+").write(ujson.dumps(template, indent=4))
        except Exception as e:
            print(f"Failed to create new config file due to {e}")

    def add(
        self,
        url: str,
        download: bool = False
        ) -> None:
        '''
        Adds the following url to the mirror and downloads the video(s)
        '''
        type = parser.link_type(url)    # Determine the type of the url
        if type == "channel":
            self.channels.append(url)
        elif type == "playlist":
            self.playlists.append(url)
        elif type == "video":
            self.singles.append(url)
        else:
            print(f"Invalid url {url}")
            return
        if download:
            self.sync()
        print(f"Added {type} to the mirror from {url}")
        # Do I wanna add to json and then sync? Or 

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
        to_download = list()    # Make a list of videos to download
        # Check if the database exists
            # If no database, create a new one
        # conn = databaser.connect_db(self.dbpath)
        # db = SqliteDict(self.dbpath)
        # Look through channels
            # For each video in channel
                # Compare against database
                    # If file does not exist
                        # Mark video for download
        # Look through playlists
            # For each video in playlist
                # Compare against database
        # Look through singles
        # Check if table exists
        # if not databaser.table_exists(conn, 'singles'):
        #     databaser.create_table(conn, 'singles')
        # Mark singles for download
        singles = SqliteDict(self.dbpath, tablename='singles', autocommit=True)
        for single in self.singles:
            # Compare against database
            url = single['url']
            key = parse.quote_plus(url)
            print(single)
            if key not in singles:
                to_download.append(single)

        print(f"{len(to_download)} Videos to download")
        # Download videos
        
        if len(to_download) > 0:
            print("Downloading videos...")
            for video in tqdm(to_download):
                output_path = self.root + 'singles/'    # Set to the single path
                url = video['url']                      # Get the url      
                filepath = downloader.download_video(url=url, output_path=output_path)
                # Add to database
                key = parse.quote_plus(url)             # Make the key good for sqlite    
                singles[key] = {"url": url, "filepath": filepath}   # Add to sqlite

    def check(
        self
        ) -> None:
        '''
        Verifies which videos in the mirror are still available from Youtube
        '''
        pass

    def show(
        self
        ) -> None:
        '''
        Prints the current state of the mirror
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