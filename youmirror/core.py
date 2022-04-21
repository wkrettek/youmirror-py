import youmirror.downloader as downloader   # Does the downloading
import youmirror.configurer as configurer   # Manages the config file
import youmirror.databaser as databaser     # Manages the database
import youmirror.printer as printer         # Manages printing to the console
import youmirror.filer as filer             # Manages the filetree
import youmirror.tuber as tuber             # Manages pytube objects
import logging              # Logging
from typing import Union    # For typing
from pytube import YouTube, Channel, Playlist   # Used for lots of stuff
from pathlib import Path    # Helpful for ensuring text inputs translate well to real directories
from datetime import datetime   # For marking dates
import shutil               # For removing whole directories    
from copy import deepcopy   # For deep copying dictionaries
import os                   # For calculating directory sizes

'''
This is the core module
------
# TODO I think some asyncio could be implemented here when collecting data
from the videos and waiting for youtube to respond. There might be other async
optimizations I'm not seeing too
'''

# logging.basicConfig(level=logging.DEBUG)

class YouMirror:
    '''
    Main class for maintaining a youmirror
    '''

    def __init__(
        self,
        root : str = ".",
        ) -> None:
        self.root = root                                # Root directory
        self.db_file: str = databaser.db_file           # Default name for the database file
        self.config_file: str = configurer.config_file  # Default name for the config file
        self.config: dict = None    # This stores the configs from the .toml file
        self.cache: dict[str: Union[Playlist, Channel, YouTube]] = dict() # This is used so we don't have to reinitialize pytube objects we've already made, because initializing them is slow

        self.channels_table = dict()    # Keeping our database tables open once we get them
        self.playlists_table = dict()
        self.singles_table = dict()
        self.paths_table = dict()
        self.files_table = dict()
            
    def new(self, root : str) -> None:
        '''
        Create a new mirror the given root directory
        '''

        if not root: root = self.root   # If no root is given, use the default directory

        # Get our wrapped up Paths
        path = Path(root)
        config_path = path/Path(self.config_file)
        db_path = path/Path(self.db_file)
        
        # Create all the necessary files if they don't exist (path, config, db)
        if not path.is_dir():
            print(f"Creating new mirror directory \'{path}\'")
            filer.create_path(path)
        else:
            print(f"Mirror directory \'{path}\' already exists")
        if not config_path.is_file():
            print(f"Creating config file \'{config_path}\'")
            configurer.new_config(config_path, root)
        else:
            print(f"Config file \'{config_path}\' already exists")
        if not db_path.is_file():
            print(f"Creating database \'{db_path}\'")
            filer.create_file(db_path)
        else:
            print(f"Database \'{db_path}\' already exists")

    def add(self, url: str, root: str = None, **kwargs) -> None:
        '''
        Adds the url to the mirror and downloads the video(s)
        '''

        # Initialize root
        if not root: root = self.root
        path = Path(root)

        # Config setup
        config_path = path/Path(self.config_file)   # Get the config file & ensure it exists
        db_path = path/Path(self.db_file)                # Get the db file & ensure it exists
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
            if not (yt_string := tuber.link_type(url)):             # Get the url type (channel, playlist, single)
                print(f"Invalid url \'{url}\'")
                return
            if not (id := tuber.link_id(url)):                      # Get the id from the url
                print(f'Could not parse id from url \'{url}\'')
                return
            if configurer.yt_exists(yt_string, id, self.config):    # Check if the link is already in the mirror
                print(f'url \'{url}\' already exists in the mirror')
                return
            if not (yt := self.get_pytube(url, self.cache)):     # Get the proper pytube object                    
                print(f'Could not parse url \'{url}\'')
                return
        except Exception as e:
            logging.exception(f"Could not parse url {url} due to {e}")

        # Collect the specs
        try:
            name = tuber.get_name(yt)  # Get the name of the pytube object
            url = tuber.get_url(yt)    # We need to get the url from pytube object in case someone passes a dirty url (like a video from a playlist)                        
            last_updated = datetime.now().strftime('%Y-%m-%d')  # Mark today's date as the last updated
        except Exception as e:
            logging.exception(f"Failed to collect specs from url error: {e}")
        specs = {"name": name, "url": url, "last_updated": last_updated, "resolution" :active_options["resolution"]}

        # Add the id to the config
        yt_string = tuber.yt_to_type_string(yt)    # Get the yt type string
        print(f"Adding {url} to the mirror")
        logging.info(f"Adding {url} to the mirror")
        self.config[yt_string][id] = specs          # TODO doing it directly for now, but we should go through the configurer
        # configurer.add_yt(yt_string, id, self.config, specs)  # Add the url to the config # TODO TODO TODO
        to_add: list[Union[Channel, Playlist, YouTube]] = []    # Create list of items to add       
        to_add.append(yt)                                       # Mark it for adding

        paths_table = databaser.get_table(db_path, "paths") # Need this to resolve collisions (only checking paths)

        # Add the items to the database
        to_download: list[YouTube] = []         # List of items to download
        paths_to_add = dict()                   # Local dict of paths before we commit to db
        singles_to_add = dict()                 # Local dict of singles to add before committing to db
        files_to_add = dict()                   # Local dict of files before we commit to db
        for item in to_add:                     # Search through all the pytube objects we want to add
            keys = tuber.get_keys(item, dict(), active_options, paths_table)    # Get all the keys to add to the table
            print(f'Adding {yt_string} \'{keys["name"]}\'')
            logging.debug(f"Adding {keys} to the database")

            paths_to_add.update({keys["path"]: {"parent": id}})        # Add the path to the paths dict
            if "files" in keys:             # This means we passed a single
                to_download.append(item)    # Mark it for downloading
                singles_to_add[id] = keys      # Add the single to be added later  
                files = deepcopy(keys["files"])  # Copy the files dict
                for filepath in files:  # Add some extra info we only want in the files table
                    file = files[filepath] 
                    file["parent"] = id
                    file["downloaded"] = False
                    files_to_add[filepath] = file # Add the files to the local dict

            # Handle children
            if "children" in keys:                              # If any children appeared when we got keys
                print(f'Found {len(keys["children"])} Youtube videos')

                for child in tuber.get_children(item):   # We have to get the children again to get urls instead of ids :/

                    inject_keys = {"parent_id": id, "parent_name": 
                    keys["name"], "parent_type": yt_string, "path": keys["path"]}       # passing in parent info
                    child = self.get_pytube(child, self.cache)    # Wrap those children in pytube objects
                    to_download.append(child)           # Mark this YouTube object for downloading
                    child_id = tuber.get_id(child)     # Get the id for the single

                    child_keys = tuber.get_keys(child, inject_keys, active_options, paths_table) # Get the rest of the keys from the pytube object

                    singles_to_add[child_id] = child_keys                           # Mark the single to be added
                    print(f'Adding \'{child_keys["name"]}\'')
                    logging.debug(f"Adding {child_keys} to the database")

                    paths_to_add.update({child_keys["path"]: {"parent": child_id}}) # Mark the path to be added
                    logging.debug(f'Adding path {child_keys["path"]} with id {child_id}')

                    files = deepcopy(child_keys["files"])    # Copy the files dict
                    for filepath in files:    # Add some extra info we only want in the files table
                        file = files[filepath]
                        file["parent"] = child_id
                        file["downloaded"] = False
                        logging.debug((f'Adding file {filepath} with keys {file}'))
                        files_to_add[filepath] = file   # Add the files to the local dict   

        # Calculate download size
        download_size: int = 0
        if not kwargs.get("no_dl", False):
            for item in to_download:
                single =  singles_to_add[tuber.get_id(item)]  # Get the keys for the single
                for filename in single["files"]:        # Get the filenames
                    file_type = files_to_add[filename]["type"] # Get the file type "video", "audio", "caption"
                    print(f"Calculating filesize for {file_type} {str(Path(filename).name)}")
                    filesize = downloader.calculate_filesize(item, file_type, active_options)   # Get the filesize
                    files_to_add[filename]["filesize"] = filesize  # Record the filesize in the db
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
            singles_to_add[id] = keys  # Else, add it to the singles pile
        singles_table = databaser.get_table(db_path, "single")  # Where yt videos go
        files_table = databaser.get_table(db_path, "files")  # Where files go
        # Commit to database
        files_table.update(files_to_add)       # Record the files in the database
        paths_table.update(paths_to_add)       # Record the paths in the database
        singles_table.update(singles_to_add)   # Record all the singles
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
            id = tuber.get_id(item)        # Get the id
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
        
        # if not kwargs.get("no_dl", False):
            # self.sync(root=root, url=url)   # Sync all the files for this url instead of doing it in this func TODO TODO TODO

        print("Done!")

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
        db_path = path/Path(self.db_file)                # Get the db file & ensure it exists

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
        try:
            yt_string = tuber.link_type(url)     # Get the url type (channel, playlist, single)
            id = tuber.link_id(url)                         # Get the id from the link
            yt = self.get_pytube(url, self.cache)          # Get the proper pytube object
        except Exception as e:
            logging.exception('Could not get info for url \'%s\' due to e', url, e)

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
        yt_string = tuber.link_type(url)   # Get the type of youtube object "channel", "playlist", "single"
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
            path = singles_table[single]["path"]
            paths_to_remove.add(path)
            # print(f'Path for single {single} = {path}')
            for filename in singles_table[single]["files"].keys():
                files_to_remove.add(filename)
            # print("Files = ", singles_table[single]["files"])

        print(f'removing {len(singles_to_remove)} singles')
        print(f'removing {len(paths_to_remove)} paths')
        print(f'removing {len(files_to_remove)} files')

        print("Saving changes...")
        # Open databases
        files_table = databaser.get_table(db_path, "files", autocommit=False) # Get the files table
        paths_table = databaser.get_table(db_path, "paths", autocommit=False) # Get the paths table        

        # Commit the changes to the database
        for path in paths_to_remove:        # Remove the paths from the database
            del paths_table[path]
        for file in files_to_remove:        # Delete the files from the database
            del files_table[file]
        for single in singles_to_remove:    # Delete the singles from the database
            del singles_table[single]
        if yt_string != "single":           # If it's a playlist or a channel
            del table[id]                   # Delete the object from the database
        files_table.commit()                # Commit the changes to the database          
        singles_table.commit()
        table.commit()

        # Update config file
        del self.config[yt_string][id]  # TODO doing it directly for now, 
        # but we should go through the configurer
        configurer.save_config(config_path, self.config)
        
    def sync(self, root: str = None, url: str = None, **kwargs: dict) -> None:
        '''
        Syncs the mirror against the database
        '''

        if not root:
            root = self.root

        # if not kwargs.get("update"):   # Update if specified
        # self.update(root)

        # if url: # If a url is specified, just sync that
        #     print(f"Synced with \'{url}\'!")
        #     return url


        # Config setup
        path = Path(root)
        config_path = path/Path(self.config_file)   # Get the config file & ensure it exists
        db_path = path/Path(self.db_file)                # Get the db file & ensure it exists

        if not config_path.is_file():                           # Verify the config file exists   
            logging.error('Could not find config file in root directory \'%s\'', path)
            return
        if not db_path.is_file():                               # Verify the database file exists
            logging.error('Could not find database file in root directory \'%s\'', path)
            return
        self.config = configurer.load_config(config_path)       # Load the config file
        active_options = configurer.defaults                                # Load default options
        global_options = configurer.get_options("youmirror", self.config)   # Get global options from config
        active_options.update(global_options)                               # Overwrite with globals
        # active_options.update(kwargs)                                       # Overwrite with command line options
        active_options["has_ffmpeg"] = shutil.which("ffmpeg") is not None   # Record whether they have ffmpeg

        to_download = list()    # Make a list of videos to download

        channels = self.config["channel"]   # Get all the channels
        playlists = self.config["playlist"] # Get all the playlists
        singles = self.config["single"]     # Get all the singles

        files_to_download = dict()
        files_table = databaser.get_table(db_path, "files", autocommit=True)
        for filepath in files_table:                            # Search through the files table and find undownloaded files
            file = files_table[filepath]                        # Get the file keys
            downloaded = file["downloaded"]                     # Record if downloaded
            # print("Checking file with keys ", file)
            if not downloaded:                                  # If not downloaded, mark it for downloading
                files_to_download[filepath] = file
                # filename = Path(filepath).name  # Get the filename for pretty printing
                # print(f"marking {filename} for download")

        print(f'Found {len(files_to_download)} files to download')
        
        # Download all the files
        singles_table = databaser.get_table(db_path, "single")    
        if len(files_to_download) > 0:
            print("Downloading videos...")   
            for filepath in files_to_download:          # Search through all the pytube objects we want to download
                filename = str(Path(filepath).name)
                # print("Downloading ", filename)
                file = files_to_download[filepath]      # Get keys for the filepath
                logging.debug(f'Keys for file {filename} are {file}')
                id = file["parent"]                     # Get the id for the parent
                if id not in self.cache:
                    url = singles_table[id]["url"]      # Get the url for the id in the database
                    if id not in self.cache:                # Check if the cache has the yt object
                        yt = self.get_pytube(url, self.cache)         # Get the yt object
                        self.cache.update({id: yt})         # Add the id and the yt object to the cache
                    else:
                        yt = self.cache[id]             # Otherwise grab the yt object from the cache
                file_type = file["type"]        # Get the file type 
                if file_type == "caption":      # If it's a caption, use options to set the caption language
                    active_options["caption_type"] = file["caption_type"] # Set the caption type
                if not Path(filepath).exists():     # If the file doesn't exist
                    filepath = str(path/Path(filepath)) # Inject the root that was passed from the add() function call
                    if downloader.download_single(yt, file_type, filepath, active_options): # Download it
                        file["downloaded"] = True # If successful mark it as downloaded
                        files_table[filepath] = file # update the files table
                        files_table.commit()


        print("All done!")


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
        db_path = path/Path(self.db_file)                # Get the db file & ensure it exists

        if not config_path.is_file():                           # Verify the config file exists   
            logging.error(f'Could not find config file in root directory \'{path}\'')
            return
        if not db_path.is_file():                               # Verify the database file exists
            logging.error(f'Could not find database file in root directory \'{path}\'')
            return
        self.config = configurer.load_config(config_path)       # Load the config file

        channels = configurer.get_options("channel", self.config)   # Load channels
        playlists = configurer.get_options("playlist", self.config)   # Load channels

        channels_table = databaser.get_table(db_path, "channel")   # Load channels table
        playlists_table = databaser.get_table(db_path, "playlist") # Load playlists table

        # For each item in channels
        for id in channels:
            channel = channels[id]
            print("id ==", id)
            url = channel["url"]    # Get the url
            print("url ==" ,url)
            yt = self.get_pytube(url, self.cache)  # Get the pytube object
            children = tuber.get_children(yt)      # Get children urls
            db_channel = channels_table[id] # Get the channel from the db
            db_children = db_channel["children"]    # Get the children in the database
            print(len(children) == len(db_children)) # Determine whether there are new videos
            if len(children) != len(db_children):    # If there are new videos, add them to the database
                db_children.update(children)


        print("All set!")
        to_download: set[YouTube] = set()
        return to_download  

    def verify(self) -> None:
        '''
        Verifies the integrity of the mirror (somehow)
        '''
        return

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
        print('TYPE --- NAME --- URL')
        print('-'* 30)

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
        return

    def _add_yt(self, url: str) -> None:
        '''
        Adds the url and its info to the database
        '''
        return

    def _remove_yt(self, url: str) -> None:
        '''
        Removes a url and its info from the database
        '''
        return

    def get_pytube(self, url: str, cache: dict) -> None:
        '''
        Returns a new pytube object or one from the cache
        '''
        try:
            if url in cache:        # If the url is already cached, return its object
                return cache[url]
            else:
                pytube = tuber.new_pytube(url)  # Get new pytube object
                cache[url] = pytube             # Cache it
        except Exception as e:
            logging.exception('Could not get pytube object for %s due to', url, e)

    def get_keys():
        '''
        Gets the keys for the url before adding to the database
        '''
