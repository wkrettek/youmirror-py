import youmirror.parser as parser
import youmirror.downloader as downloader
import youmirror.helper as helper
import youmirror.configurer as configurer
import youmirror.databaser as databaser
import youmirror.printer as printer
import logging              # Logging
from typing import Union    # For typing
from pytube import YouTube, Channel, Playlist
from pathlib import Path    # Helpful for ensuring text inputs translate well to real directories
from datetime import datetime
import shutil               # For removing whole directories    
from copy import deepcopy   # For deep copying dictionaries
import os

'''
This is the core module
------
# TODO I think some asyncio could be implemented here when collecting data
from the videos and waiting for youtube to respond. There might be other async
optimizations I'm not seeing too
'''

logging.basicConfig(level=logging.DEBUG)

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

        if not root:    # If no root is given, use the current directory
            root = self.root

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

        # Initialize root
        if not root: root = self.root
        path = Path(root)

        # Config setup
        config_path = path/Path(self.config_file)   # Get the config file & ensure it exists
        db_path = path/Path(self.db)                # Get the db file & ensure it exists
        if not config_path.is_file():               # Verify the config file exists   
            logging.error(f'Could not find config file in directory \'{path}\'')
            return
        if not db_path.is_file():                   # Verify the database file exists
            logging.error(f'Could not find database file in directory \'{path}\'')
            return

        # Load the config
        try:
            self.config = configurer.load_config(config_path)
        except Exception as e:
            logging.exception(f"Could not load given config file due to {e}")
            return

        # Load the options from config
        active_options = configurer.defaults                                # Load default options
        global_options = configurer.get_options("youmirror", self.config)   # Get global options
        active_options.update(global_options)                               # Overwrite with globals
        active_options.update(kwargs)                                       # Overwrite with command line options
        if active_options["resolution"] not in downloader.resolutions:
            logging.error(f"Invalid resolution \'{active_options['resolution']}\', valid resolutions = {downloader.resolutions}")                                      # Validate resolution
            return
        active_options["has_ffmpeg"] = shutil.which("ffmpeg") is not None   # Record whether they have ffmpeg
        # self.config.update({"resolution": active_options["resolution"]})
        logging.debug("Active options:", active_options)


        # Parse the url & create pytube object
        try:
            if not(yt_string := parser.link_type(url)):             # Get the url type (channel, playlist, single)
                print(f"Invalid url \'{url}\'")
                return
            if not(id := parser.link_id(url)):                      # Get the id from the url
                print(f'Could not parse id from url \'{url}\'')
                return
            if configurer.yt_exists(yt_string, id, self.config):    # Check if the link is already in the mirror
                print(f'url \'{url}\' already exists in the mirror')
                return
            if not (yt := parser.get_pytube(url)):                             # Get the proper pytube object
                print(f'Could not parse url \'{url}\'')
                return
        except Exception as e:
            logging.exception(f"Could not parse url {url} due to {e}")

        # Collect the specs
        try:
            id = parser.link_id(url)                # Get the id of the pytube object
            name = parser.get_name(yt)              # Get the name of the pytube object
            url = parser.get_url(yt)                # Get the url of the pytube object
            last_updated = datetime.now().strftime('%Y-%m-%d')     # Get the date of the pytube object
        except Exception as e:
            logging.exception(f"Failed to collect specs from url error: {e}")
        specs = {"name": name, "url": url, "last_updated": last_updated}
        if "resolution" in kwargs: specs.update({})   # Add resolution to configs if specified # TODO actually add it

        # Add the id to the config
        to_add: list[Union[Channel, Playlist, YouTube]] = []    # Create list of items to add
        yt_string = parser.yt_to_type_string(yt)                # Get the yt type string

        print(f"Adding {url} to the mirror")        
        logging.info(f"Adding {url} to the mirror")
        self.config[yt_string][id] = specs                  # TODO doing it directly for now, but we should go through the configurer
        # configurer.add_yt(yt_string, id, self.config, specs)       # Add the url to the config # TODO TODO TODO
        to_add.append(yt)                                            # Mark it for adding


        paths_table = databaser.get_table(db_path, "paths") # Need this to resolve collisions (only checking paths)
        singles = dict()                                    # Create a dict of singles

        # Add the items to the database
        to_download: list[YouTube] = []         # List of items to download
        paths_to_add = dict()                   # Local dict of paths before we commit to db
        singles_to_add = dict()                 # Local dict of singles to add before committing to db
        files_to_add = dict()                   # Local dict of files before we commit to db
        for item in to_add:                     # Search through all the pytube objects we want to add
            keys = parser.get_keys(item, dict(), active_options, paths_table)    # Get all the keys to add to the table
            print(f'Adding {yt_string} \'{keys["name"]}\'')
            logging.debug(f"Adding {keys} to the database")

            paths_to_add.update({keys["path"]: {"parent": id}})        # Add the path to the paths dict
            if "files" in keys:             # This means we passed a single
                to_download.append(item)    # Mark it for downloading
                singles[id] = keys      # Add the single to be added later  
                files_to_add = deepcopy(keys["files"])  # Copy the files dict
                for filepath in files_to_add:  # Add some extra info we only want in the files db
                    file = files_to_add[filepath] 
                    file["parent"] = id
                    file["downloaded"] = False
                    files[filepath] = file # Add the files to the local dict

            # Handle children
            if "children" in keys:                              # If any children appeared when we got keys
                inject_keys = {"parent_id": id, "parent_name": 
                keys["name"], "parent_type": yt_string, "path": keys["path"]}       # passing in parent info
                print(f'Found {len(keys["children"])} Youtube videos')

                for child in parser.get_children(item):   # We have to get the children again to get urls instead of ids :/

                    child = parser.get_pytube(child)    # Wrap those children in pytube objects
                    to_download.append(child)           # Mark this YouTube object for downloading
                    child_id = parser.get_id(child)     # Get the id for the single

                    child_keys = parser.get_keys(child, inject_keys, active_options, paths_table) # Get the rest of the keys from the pytube object
                    paths[keys["path"]] = {}        # Add the path to the paths dict
                    print(f'Adding \'{child_keys["name"]}\'')
                    logging.debug(f"Adding {child_keys} to the database")
                    singles[child_id] = child_keys      # Add the single to be added later
                    logging.info(f"Adding {child} to the database")
                    files_to_add = deepcopy(child_keys["files"])    # Copy the files dict
                    for filepath in files_to_add:    # Add some extra info we only want in the files db
                        file = files_to_add[filepath]
                        file["parent"] = child_id
                        file["downloaded"] = False
                        files[filepath] = file   # Add the files to the local dict          

        # Calculate download size
        download_size: int = 0
        if not kwargs.get("no_dl", False):
            for item in to_download:
                single =  singles[parser.get_id(item)]  # Get the keys for the single
                for filename in single["files"]:        # Get the filenames
                    file_type = files[filename]["type"] # Get the file type "video", "audio", "caption"
                    print(f"Calculating filesize for {file_type} {str(Path(filename).name)}")
                    filesize = downloader.calculate_filesize(item, file_type, active_options)   # Get the filesize
                    files[filename]["filesize"] = filesize  # Record the filesize in the db
                    download_size += filesize           # Add the filesize to the total download size
            
            # Show download size
            download_size = printer.human_readable(download_size)   # Convert to human readable
            print(f'Downloading will add {download_size} bytes to the mirror')

        # Ask for confirmation
        if not kwargs.get("force", False) or not kwargs.get("no_dl", False):
            if input("Continue? (y/n) ") != "y":                    # Get confirmation
                print("Aborting")
                return

        print("Saving...")

        # Update config file
        configurer.save_config(config_path, self.config)

        # Open the database tables
        if yt_string in ['channel', 'playlist']:            # If it's a channel or playlist
            table = databaser.get_table(db_path, yt_string) # Get the appropriate database for the toplevel item
            table[id] = keys                                # Add it to the database
            table.commit()                                  # Commit the changes to the database
        else:
            singles[id] = keys  # Else, add it to the singles pile
        singles_table = databaser.get_table(db_path, "single")  # Where yt videos go
        files_table = databaser.get_table(db_path, "files")  # Where files go
        # Commit to database
        files_table.update(files)       # Record the files in the database
        paths_table.update(paths)       # Record the paths in the database
        singles_table.update(singles)   # Record all the singles
        files_table.commit()            # Commit the changes to the database
        paths_table.commit()            # Commit the changes to the database
        singles_table.commit()          # Commit the changes to the database

        # Check if downloading is skipped
        if kwargs.get("no_dl", False):
            print("Skipping download")
            return

        print("Downloading...")

        # Download all the files                                 
        for item in to_download:            # Search through all the pytube objects we want to download
            id = parser.get_id(item)        # Get the id
            files = singles_table[id]["files"]  # Get the files from the database
            for f in files:                  # Search through all the files
                data = files_table[f]              # Get the data for this file
                file_type = data["type"]           # Get the file type 
                if file_type == "caption":          # If it's a caption, use options to set the caption language
                    active_options["caption_type"] = data["caption_type"] # Set the caption type
                if not Path(f).exists():     # If the file doesn't exist
                    filepath = str(path/Path(f)) # Inject the root that was passed from the add() function call
                    if downloader.download_single(item, file_type, filepath, active_options): # Download it
                        files_table[f]["downloaded"] = True # If successful mark it as downloaded

    def remove(self, url: str, root: str = None, **kwargs) -> None:
        """
        Removes the following url from the mirror and deletes the video(s)
        """
        if not root:
            root = self.root

        # Config setup
        print("Setting up config")
        path = Path(root)
        config_path = path/Path(self.config_file)   # Get the config file & ensure it exists
        db_path = path/Path(self.db)                # Get the db file & ensure it exists

        print("Loading config")
        if not config_path.is_file():                           # Verify the config file exists   
            logging.error(f'Could not find config file in root directory \'{path}\'')
            return
        if not db_path.is_file():                               # Verify the database file exists
            logging.error(f'Could not find database file in root directory \'{path}\'')
            return
        self.config = configurer.load_config(config_path)       # Load the config file
        
        print("Getting pytube object")
        # Parse the url & create pytube object
        if not (yt_string := parser.link_type(url)):   # Get the url type (channel, playlist, single)
            logging.error(f'Invalid url \'{url}\'')
            return
        yt = parser.get_pytube(url)         # Get the proper pytube object
        id = parser.get_id(yt)              # Get the id for the object

        print("Getting checking for url")
        # Check if the id is already in the config
        if configurer.yt_exists(yt_string, id, self.config):
            print(f'Removing \'{yt_string}\' with id \'{id}\'')
            logging.info(f"Removing {url} from the mirror")
        else:
            print(f"{url} is not in the mirror")
            logging.info(f"Could not find {url} not found in the mirror")
            return

        print("Getting db info for url")
        yt_string = parser.link_type(url)   # Get the type of youtube object "channel", "playlist", "single"
        table = databaser.get_table(db_path, yt_string, autocommit=False)  # Get the appropriate database
        keys = table[id]                    # Get the keys for the object

        if not kwargs.get("no_rm", False):
            print("Calculating removal size")
            path = Path(root)/Path(keys["path"])                 # Get the path for the object
            path_size = 0
            files_to_remove = set()
            for root, dirs, files in os.walk(path, topdown=False):  # Find all the files in the directory
                for name in files:                                  # Search through all the files
                    filepath = os.path.join(root, name)             # Get the filepath
                    print(filepath) 
                    filepath = Path(filepath)
            print(f"Removing will delete {printer.human_readable(path_size)} from the mirror")

        # Ask for confirmation
        if (not kwargs.get("force", False)) or not kwargs.get("no_rm", False):
            if input("Continue? (y/n) ") != "y":                    # Get confirmation
                print("Aborting")
                return

        if not kwargs.get("no_rm" ,False):
            print("Deleting files...")
            shutil.rmtree(path, ignore_errors=True)                                       # Remove the directory

        print("Getting paths to remove...")
        paths_to_remove = set()
        path = keys["path"]
        paths_to_remove.add(path)
        print("Paths to remove", paths_to_remove)

        print("Getting singles to remove")
        singles_to_remove = set()
        if yt_string == "single":
            singles_to_remove.add(id)
        else:
            singles_to_remove.update(keys["children"])
        print("Singles to remove", singles_to_remove)

        print("Getting files to remove")
        files_to_remove = set()
        if not (singles_table := databaser.get_table(db_path, "single")):   # Get the singles table if not already initialized
            singles_table = table
        for single in singles_to_remove:
            print("Files = ", singles_table[single]["files"])

        # print("Cleaning database...")
        # # Open databases
        # singles_to_remove = set()   # Collect the singles
        # if not (singles_table := databaser.get_table(db_path, "single")):   # Get the singles table if not already initialized
        #     singles_table = table
        #     singles_to_remove.add(id)                       # Mark it to be removed
        # files_table = databaser.get_table(db_path, "files") # Get the files table
        # paths_table = databaser.get_table(db_path, "paths") # Get the paths table
        # if "children" in table[id]:                         # If it has children
        #     children = table[id]["children"]                # Get the children
        #     for child in children:                          # Search through all the children
        #         singles_to_remove.add(child)                # Mark each child to be removed

        # # Collect the filepaths from the singles
        # for single in singles_to_remove:
        #     files = singles_table[single]["files"]
        #     for file in files:
        #         files_to_remove.add(file)

        # print("files to remove", files_to_remove)
        

        # print("Saving changes...")
        # # Commit the changes to the database
        # del paths_table[keys["path"]]                             # Remove the path from the database
        # for file in files_to_remove:
        #     del files_table[file]                                 # Delete the files from the database
        # for single in singles_to_remove:
        #     del singles_table[single]                             # Delete the singles from the database
        # del table[id]                                             # Delete the object from the database
        # files_table.commit()                                    # Commit the changes to the database          
        # singles_table.commit()
        # table.commit()

        # Update config file
        del self.config[yt_string][id]  # TODO doing it directly for now, but we should go through the configurer
        configurer.save_config(config_path, self.config)

    
    def sync(
        self,
        root: str = None,
        ) -> None:
        '''
        Syncs the mirror against the config file
        '''

        if not root:
            root = self.root

        self.update(root)

        # Config setup
        path = Path(root)
        config_path = path/Path(self.config_file)   # Get the config file & ensure it exists
        db_path = path/Path(self.db)                # Get the db file & ensure it exists

        if not config_path.is_file():                           # Verify the config file exists   
            logging.error(f'Could not find config file in root directory \'{path}\'')
            return
        if not db_path.is_file():                               # Verify the database file exists
            logging.error(f'Could not find database file in root directory \'{path}\'')
            return
        self.config = configurer.load_config(config_path)       # Load the config file

        to_download = list()    # Make a list of videos to download

        channels = self.config["channel"]   # Get all the channels
        playlists = self.config["playlist"] # Get all the playlists
        singles = self.config["single"]     # Get all the singles

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

    def update(
        self,
        root: str = None
        ) -> None:
        '''
        Updates the database without downloading anything (returns objects to download if you so choose)
        '''
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
            return
        self.config = configurer.load_config(config_path)       # Load the config file

        channels = configurer.get_options("channel", self.config)   # Load channels
        playlists = configurer.get_options("channel", self.config)   # Load channels

        channels_table = databaser.get_table(db_path, "channels")   # Load channels table
        playlists_table = databaser.get_table(db_path, "playlists") # Load playlists table

        for id in channels:
            channel = channels[id]
            print("id ==", id)
            url = channel["url"]    # Get the url
            print("url ==" ,url)
            yt = parser.get_pytube(url)  # Get the pytube object
            children = parser.get_children(yt)      # Get children urls
            db_channel = channels_table[id] # Get the channel from the db
            db_children = db_channel["children"]    # Get the children in the database
            print(len(children) == len(db_children)) # Determine whether there are new videos
            if len(children) != len(db_children):    # If there are new videos, add them to the database
                db_children.update(children)


        print("All set!")
        to_download = set()
        return to_download  

    def verify(
        self
        ) -> None:
        '''
        Verifies the integrity of the mirror (somehow)
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
            print(f"Could not load config file in directory \'{root}\'")
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