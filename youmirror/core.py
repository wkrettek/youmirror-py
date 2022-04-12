import youmirror.parser as parser
import youmirror.downloader as downloader
import youmirror.helper as helper
from typing import (
    Optional
)
import logging
import sqlite3
from urllib import parse
from sqlitedict import SqliteDict
import ujson
from pytube import YouTube, Channel, Playlist
from pathlib import Path    # Helpful for ensuring text values translate well to real directories
from tqdm import tqdm
import symbol
import os

# This is the main class for maintaining a youmirror
class YouMirror:

    def __init__(
        self,
        root : str = ".",
        ) -> None:
        self.root = root
        self.db = 'youmirror.db'
        self.dbpath = self.root + self.db
        self.config_file = 'youmirror.json'
        self.configpath = self.root + self.db
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
        # Load all types of mirrables
        self.channels = config['channels']
        self.playlists = config['playlists']
        self.singles = config['singles']

    def to_json(self) -> None:
        """
        Writes all the values from the YouMirror object into the config file
        """
        # Get the config file
        configpath = self.configpath
        urls = set()
        try:
            json = ujson.load(open(configpath))
        except Exception as e:
            print(e)
        # Collect urls in 
        for json_channels in json["channels"]:
            urls.add(json_channels["url"])
        # Look through channels
            #
        # Look through playlists
        # Look through singles

        pass

    # Needs a little work, the root directory string gets printed strangely when filling out the template
    def new(
        self,
        root : str = "./ym/"
        ) -> None:
        '''
        Create a new mirror directory at the given path
        '''
        config_file = self.config_file
        db = self.db
        
        # Create all the necessary files
        if not helper.path_exists(root):                                # Check if the path exists
            logging.info(f"Creating new mirror directory at {root}")
            helper.create_path(root)                                    # If it doesn't, create it
        if not helper.file_exists(root, config_file):                   # Check if the config file exists
            logging.info(f"Creating config file at {root + config_file}")
            helper.create_file(root, config_file)                       # If it doesn't, create it
        if not helper.file_exists(root, db):                            # Check if the database exists
            logging.info(f"Creating database at {root + db}")
        helper.create_file(root, db)                                    # If it doesn't create it

        # Fill out the config file with a template
        try:
            from youmirror.template import template
            path = Path(root)       # Wrap it to ensure it's 
            filepath = path/Path(config_file)
            filepath.open(mode = "w").write(ujson.dumps(template, indent=4))
        except Exception as e:
            print(f"Failed to create new config file due to {e}")

    def add(
        self,
        url: str,
        root: str,
        download: bool = False
        ) -> None:
        '''
        Adds the following url to the mirror and downloads the video(s)
        '''
        config_file = helper.get_config(root)
        self.from_json(config_file)
        print(f'channels are {self.channels}')
        # type = parser.link_type(url)    # Determine the type of the url
        # if type == "channel":
        #     self.channels.append(url)
        # elif type == "playlist":
        #     self.playlists.append(url)
        # elif type == "video":
        #     self.singles.append(url)
        # else:
        #     print(f"Invalid url {url}")
        #     return
        # if download:
        #     self.sync()
        # print(f"Added {type} to the mirror from {url}")
        # # Do I wanna add to json and then sync? Or 

    def remove(
        self,
        url: str
        ) -> None:
        """
        Removes the following url from the mirror and deletes the video(s)
        """
        # Search for json file

    
    def sync(
        self,
        config_file: str
        ) -> None:
        '''
        Syncs the mirror against the config file
        '''
        # Search for json file
        # If it exists
            # Switch to the directory 
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


# Must be inside root directory:
    # Config file
    # Database file

# I'd like to make download_single robust and have the other two call on it I think
# Database name should be youmirror.db
# | -- root
#       youmirror.json
#       youmirror.db
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