import youmirror.parser as parser
import youmirror.downloader as downloader
import youmirror.helper as helper
import youmirror.configurer as configurer
import youmirror.databaser as databaser
import logging              # Logging
from typing import Union    # For typing
from pytube import YouTube, Channel, Playlist
from pathlib import Path    # Helpful for ensuring text inputs translate well to real directories
import shutil               # For removing whole directories     

'''
This is the core module
------
# TODO I think some asyncio could be implemented here when collecting data
from the videos and waiting for youtube to respond. There might be other async
optimizations I'm not seeing too
'''

logging.basicConfig(level=logging.INFO)

class YouMirror:
    '''
    Main class for maintaining a youmirror
    '''

    def __init__(
        self,
        root : str = ".",
        ) -> None:
        self.root = root
        self.db: str = databaser.db_file
        self.config_file: str = configurer.config_file
        self.config = dict()
            
    def new(self, root : str) -> None:
        '''
        Create a new mirror directory at the given path
        '''

        # Get our wrapped up Paths
        path = Path(root)
        config_path = path/Path(self.config_file)
        db_path = path/Path(self.db)
        
        # Create all the necessary files if they don't exists (path, config, db)
        if not path.is_dir():
            logging.info(f"Creating new mirror directory \'{path}\'")
            helper.create_path(path)
        if not config_path.is_file():
            logging.info(f"Creating config file \'{config_path}\'")
            configurer.new_config(config_path, root)
        if not db_path.is_file():
            logging.info(f"Creating database \'{db_path}\'")
            helper.create_file(db_path)

    def add(self, url: str, root: str = None, **kwargs) -> None:
        '''
        Adds the url to the mirror and downloads the video(s)
        '''
        if not root:
            root = self.root
        path = Path(root)
        # Config setup
        config_path = path/Path(self.config_file)   # Get the config file & ensure it exists
        db_path = path/Path(self.db)                # Get the db file & ensure it exists
        if not config_path.is_file():                           # Verify the config file exists   
            logging.error(f'Could not find config file in root directory \'{path}\'')
            return
        if not db_path.is_file():                               # Verify the database file exists
            logging.error(f'Could not find database file in root directory \'{path}\'')
        # Load the config
        try:
            self.config = configurer.load_config(config_path)
        except Exception as e:
            logging.exception(f"Could not load given config file due to {e}")

        # Load the options from config
        active_options = configurer.defaults                                # Load default options
        global_options = configurer.get_options("youmirror", self.config)   # Get global options
        active_options.update(global_options)                               # Overwrite with globals
        # active_options.update(kwargs)                                     # Overwrite with command line options
        logging.debug("Active options:", active_options)

        # Parse the url & create pytube object
        try:
            if not(url_type := parser.link_type(url)):       # Get the url type (channel, playlist, single)
                return
            yt = parser.get_pytube(url)             # Get the proper pytube object
        except Exception as e:
            logging.exception(f"Could not parse url {url} due to {e}")

        # Collect the specs
        try:
            id = parser.get_id(yt)                  # Get the id of the pytube object
            name = parser.get_name(yt)              # Get the name of the pytube object
            url = parser.get_url(yt)                # Get the url of the pytube object
        except Exception as e:
            logging.exception(f"Failed to collect specs from url error: {e}")
        specs = {"name": name, "url": url, "type": url_type}
        
        # Add the id to the config
        to_add: list[Union[Channel, Playlist, YouTube]] = []    # Create list of items to add
        yt_string = parser.yt_to_type_string(yt)                # Get the yt type string
        if configurer.yt_exists(yt_string, id, self.config):
            logging.info(f"{url} already exists in the mirror")
            return                                              # End command here if the url is already in the mirror
        else:
            logging.info(f"Adding {url} to the mirror")
            self.config[yt_string][id] = specs                  # TODO doing it directly for now, but we should go through the configurer
            # configurer.add_yt(yt_string, id, self.config, specs)       # Add the url to the config # TODO TODO TODO
            to_add.append(yt)                                            # Mark it for adding

        # Open the database tables
        channels_table = databaser.get_table(db_path, "channels")
        playlists_table = databaser.get_table(db_path, "playlists")
        singles_table = databaser.get_table(db_path, "singles")
        filetree_table = databaser.get_table(db_path, "filetree")

        string_to_table = {"channel": channels_table, "playlist": playlists_table, "single": singles_table}  # Translation dict for pytube type to db table

        # Add the items to the database
        to_download: list[YouTube] = []     # List of items to download
        for item in to_add:                 # Search through all the pytube objects we want to add
            keys = parser.get_keys(item, dict(), active_options, dict())    # Get all the keys to add to the table
            print("Keys:", keys)
            table = string_to_table[yt_string]  # Get the appropriate table for the object
            table[id] = keys                    # Add the item to the database
            logging.info(f"Adding {url} to the database")

            if "files" in keys:             # This means we passed a single
                to_download.append(item)    # Mark it for downloading
                files = keys["files"]       # Get the files from the keys
                for file in files:
                    filetree_table[file] = {"type": "file"}
                    logging.info(f"Adding {file} to the database")

            if "children" in keys:                              # If any children appeared when we got keys
                item_path = next(iter(keys["paths"]))          # Get a calculated path from the keys
                item_path = item_path.split("/")[1:]            # Split the first bit off
                item_path = "/".join(item_path)                 # Join the list back together
                filetree_table[item_path] = {"type": "path"}    # Record the path in the filetree table

                # Get parent info to pass to children   
                parent_id = parser.get_id(item)     # Get parent's id
                parent_name = parser.get_name(item) # Get parent's name

                for child in parser.get_children(item):   # We have to get the children again to get urls instead of ids :/

                    child_keys = {"parent_id": parent_id, "parent_name": 
                    parent_name, "parent_type": yt_string, "path": item_path}       # passing this to get_keys()

                    child = parser.get_pytube(child)    # Wrap those children in pytube objects
                    to_download.append(child)           # Mark this YouTube object for downloading
                    child_id = parser.get_id(child)     # Get the id for the single

                    child_keys = parser.get_keys(child, child_keys, active_options, filetree_table) # Get the rest of the keys from the pytube object
                    # print("Child keys:", child_keys)
                    print(f'Adding child {child_id} and {child_keys} to singles table')
                    singles_table[child_id] = child_keys    # Add child to the database
                    logging.info(f"Adding {child} to the database")
                    files = child_keys["files"]             # Get the files from the keys
                    for file in files:
                        filetree_table[file] = {"type": "file"}
                        logging.info(f"Adding {file} to the database")  

        # Update config file
        configurer.save_config(config_path, self.config)                                  

        # If not forced, report how much downloading there is to do and ask for confirmation
        if not kwargs.get("dry_run", False):    # Check for a dry run
            for item in to_download:            # Search through all the pytube objects we want to download
                id = parser.get_id(item)        # Get the id
                files = singles_table[id]["files"]  # Get the files from the database
                for file in files:                  # Search through all the files
                    if not Path(file).exists():     # If the file doesn't exist
                        file = str(path/Path(file)) # Inject the root that was passed from the add() function call
                        downloader.download_single(item, file, active_options) # Download it

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

        # Config setup
        path = Path(root)
        config_path = path/Path(self.config_file)   # Get the config file & ensure it exists
        db_path = path/Path(self.db)                # Get the db file & ensure it exists

        if not config_path.is_file():                           # Verify the config file exists   
            logging.error(f'Could not find config file in root directory \'{path}\'')
            return
        if not db_path.is_file():                               # Verify the database file exists
            logging.error(f'Could not find database file in root directory \'{path}\'')
        self.config = configurer.load_config(config_path)       # Load the config file
        
        # Parse the url & create pytube object
        if not (yt_string := parser.link_type(url)):   # Get the url type (channel, playlist, single)
            logging.error(f'Invalid url \'{url}\'')
            return
        yt = parser.get_pytube(url)         # Get the proper pytube object
        id = parser.get_id(yt)              # Get the id for the object

        # Check if the id is already in the config
        if configurer.yt_exists(yt_string, id, self.config):
            logging.info(f"Removing {url} from the mirror")
        else:
            logging.info(f"Could not find {url} not found in the mirror")
            return

        # Open the database tables
        channels_table = databaser.get_table(db_path, "channels")
        playlists_table = databaser.get_table(db_path, "playlists")
        singles_table = databaser.get_table(db_path, "singles")
        filetree_table = databaser.get_table(db_path, "filetree")

        string_to_table = {"channel": channels_table, "playlist": playlists_table, "single": singles_table}  # Translation dict for pytube type to db table
        # Find the id in the database
        table = string_to_table[yt_string]  # Get the appropriate table for the object

        to_remove = list[str]()             # List of filepaths to delete
        if id in table:
            if "children" in table[id]:
                pass


        # If it has children, collect those too
        # Get all the files and paths
        # Unlink all

        # Delete all the ids from the database

        # Commit to the database

        # Clear database

        # Update config file
        del self.config[yt_string][id]                  # TODO doing it directly for now, but we should go through the configurer
        # configurer.remove_yt(yt_string, id, self.config, specs)       # Add the url to the config # TODO TODO TODO
        configurer.save_config(config_path, self.config)

    
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
        # singles = SqliteDict(self.dbpath, tablename='singles', autocommit=True)
        # for single in self.singles:
        #     # Compare against database
        #     url = single['url']
        #     print(single)
        #     if key not in singles:
        #         to_download.append(single)

        # print(f"{len(to_download)} Videos to download")
        # # Download videos
        
        # if len(to_download) > 0:
        #     print("Downloading videos...")
        #     for video in to_download:
        #         output_path = self.root + 'singles/'    # Set to the single path
        #         url = video['url']                      # Get the url      
        #         filepath = downloader.download_video(url=url, output_path=output_path)
        #         # Add to database
        #         key = parse.quote_plus(url)             # Make the key good for sqlite    
        #         singles[key] = {"url": url, "filepath": filepath}   # Add to sqlite

    def check(
        self
        ) -> None:
        '''
        Verifies which videos in the mirror are still available from Youtube
        '''
        pass

    def show(self, root: str) -> None:
        '''
        Prints the current state of the mirror
        '''

        if not root:
            root = self.root

        # Load the config
        config_path = Path(root)/Path(self.config_file)   # Get the config file & ensure it exists
        self.config = configurer.load_config(config_path)
        if not self.config:
            print(f"Could not load config file in root directory {root}")
            return

        # Print the config
        channel = self.config['channel']
        playlist = self.config['playlist']
        single = self.config["single"]
        print(f'TYPE --- NAME --- URL')
        print(f'-'* 30)

        for yt in channel:
            item = channel[yt]
            name = item['name']
            url = item['url']
            print(f"channel - {name} - {url} -")

        for yt in playlist:
            item = playlist[yt]
            name = item['name']
            url = item['url']
            print(f"playlist - {name} - {url} -")

        for yt in single:
            item = single[yt]
            name = item['name']
            url = item['url']
            print(f"single - {name} - {url} -")

    def archive(self, root: str) -> None:
        '''
        Uploads the mirror to the internet archive
        TODO will add internetarchive as an optional dependency later on
        if/when this gets implemented
        '''
        pass