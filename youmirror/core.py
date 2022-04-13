import youmirror.parser as parser
import youmirror.downloader as downloader
import youmirror.helper as helper
import youmirror.configurer as configurer
import datetime
import logging
from typing import Optional
from urllib import parse
from sqlitedict import SqliteDict
import toml
from pytube import YouTube, Channel, Playlist
from pathlib import Path    # Helpful for ensuring text values translate well to real directories
from tqdm import tqdm


logging.basicConfig(level=logging.INFO)

# This is the main class for maintaining a youmirror
class YouMirror:

    def __init__(
        self,
        root : str = ".",
        ) -> None:
        self.root = root
        self.db = 'youmirror.db'
        self.config_file = 'youmirror.toml'
        self.config = dict()

    def from_toml(self, config_file: Path) -> None:
        '''
        Load a toml file into the YouMirror object
        '''
        try:
            self.config = toml.load(open(config_file))
        except Exception as e:
            logging.exception(f"Could not parse given config file due to {e}")

    def to_toml(self, config_file: str) -> None:
        """
        Writes all the values from the YouMirror object into the toml config file
        """
        # Get the config file

        try:
            path = Path(self.root)
            filepath = path/Path(config_file)                   # Wrap the path
            if filepath.exists():                               # Check if the file exists     
                toml_string = toml.dumps(self.config)           # Convert the config to a toml string
                print("New config: \n" + toml_string)           # Print the new config
                filepath.open('w').write(toml_string)   # Write the toml string to the config file
        except Exception as e:
            print(e)
            
    def new(
        self,
        root : str
        ) -> None:
        '''
        Create a new mirror directory at the given path
        '''

        # Get our wrapped up Path objects
        path = Path(root)
        config_path = helper.get_path(root, self.config_file)
        db_path = helper.get_path(root, self.db)
        
        # Create all the necessary files
        if not helper.path_exists(path):                                # Check if the path exists
            logging.info(f"Creating new mirror directory \'{path}\'")
            helper.create_path(path)                                    # If it doesn't, create it
        # Maybe put an 'already exists' message here? (for all of them)
        if not helper.file_exists(config_path):                   # Check if the config file exists
            logging.info(f"Creating config file \'{config_path}\'")
            helper.create_file(config_path)                       # If it doesn't, create it
            # Fill out the config file with a template
            try:
                from youmirror.template import template
                template["name"] = root
                template["last_updated"] = datetime.datetime.now().strftime('%Y-%m-%d')
                config_path.open(mode = "w").write(toml.dumps(template))
            except Exception as e:
                print(f"Failed to create new config file due to {e}")
        if not helper.file_exists(db_path):                            # Check if the database exists
            logging.info(f"Creating database \'{db_path}\'")
            helper.create_file(db_path)                                # If it doesn't create it



    def add(
        self,
        url: str,
        root: str = None,
        **kwargs
        ) -> None:
        '''
        Adds the following url to the mirror and downloads the video(s)
        '''
        if not root:
            root = self.root
        path = Path(root)
        # Config setup
        config_path = helper.get_path(root, self.config_file)   # Get the config file & ensure it exists
        if not helper.verify_config(config_path):               # Verify the config file   
            logging.error(f'Could not find config file in root directory \'{path}\'')
            return 
        self.from_toml(config_path)             # Build our class from the config file

        # Parse the url & create pytube object
        type = parser.check_link(url)           # Get the url type (channel, playlist, single)
        # TODO                                  # Verify the url is valid
        yt = parser.get_pytube(url, type)       # Get the proper pytube object

        # Collect the specs
        try:
            id = parser.get_id(yt)                  # Get the id of the pytube object
            name = parser.get_name(yt)              # Get the name of the pytube object
            url = parser.get_url(yt)                # Get the url of the pytube object
        except Exception as e:
            logging.exception(f"Failed to collect specs from url error: {e}")
        specs = {"name": name, "url": url, "type": type}
        
        # Add the id to the config
        if configurer.id_exists(id, type, self.config):
            logging.info(f"{url} already exists in the mirror")
        else:
            logging.info(f"Adding {url} to the mirror")
            configurer.add_item(id, specs, self.config)            # Add the url to the config
            # Mark it for downloading

        # If downloading is enabled, download the video(s)
            # If not force, report how much downloading there is to do

        # Update config file
        self.to_toml(config_path)


    def remove(
        self,
        url: str,
        root: str = None,
        **kwargs
        ) -> None:
        """
        Removes the following url from the mirror and deletes the video(s)
        """
        if not root:
            root = self.root
        path = Path(root)
        # Config setup
        config_path = helper.get_path(root, self.config_file)   # Get the config file & ensure it exists
        if not helper.verify_config(config_path):               # Verify the config file   
            logging.error(f'Could not find config file in root directory \'{config_path}\'')
            return     
        self.from_toml(config_path)             # Build our class from the config file

        # Parse the url & create pytube object
        type = parser.check_link(url)           # Get the url type (channel, playlist, single)
        # TODO                                  # Verify the url is valid
        yt = parser.get_pytube(url, type)       # Get the proper pytube object

        # Collect the specs
        try:
            id = parser.get_id(yt)                  # Get the id of the pytube object
            # name = parser.get_name(yt)              # Get the name of the pytube object
            # url = parser.get_url(yt)                # Get the url of the pytube object
        except Exception as e:
            logging.exception(f"Failed to collect specs from url error: {e}")

        # Check if the id is already in the config
        if configurer.id_exists(id, type, self.config):
            logging.info(f"Removing {url} from the mirror")
            # Remove the url from the config
            configurer.remove_item(id, self.config)
        else:
            logging.info(f"{url} not found in the mirror")

        # Update config file
        self.to_toml(config_path)

    
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