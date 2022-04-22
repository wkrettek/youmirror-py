import youmirror.downloader as downloader   # Does the downloading
import youmirror.configurer as configurer   # Manages the config file
import youmirror.databaser as databaser     # Manages the database
import youmirror.printer as printer         # Manages printing to the console
import youmirror.filer as filer             # Manages the filetree
import youmirror.tuber as tuber             # Manages pytube objects
from pytube.helpers import safe_filename    # For making good paths & filenames
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
optimizations with downloading too
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
        self.root: str = root                                       # Root directory
        self.path: Path = Path(self.root)                                # Wrap root in a path object for convenience
        self.db_file: str = databaser.db_file                       # Default name for the database file
        self.config_file: str = configurer.config_file              # Default name for the config file
        self.db_path: Path = self.path/Path(self.db_file)           # Full path for db file
        self.config_path: Path = self.path/Path(self.config_file)   # Full path for config file
        self.config: dict = dict()                                    # configs from file
        self.cache: dict[str: Union[Playlist, Channel, YouTube]] = dict() # This is used so we don't have to reinitialize pytube objects we've already made, because initializing them is slow
            
    def new(self) -> None:
        '''
        Create a new mirror the given root directory
        '''

        # Localize our paths so we don't have to type self a bunch of times
        path = self.path
        config_path = self.config_path
        db_path = self.db_path
        
        # Create all the necessary files if they don't exist (path, config, db)
        if not path.is_dir():
            print(f"Creating new mirror directory \'{path}\'")
            filer.create_path(path)
        else:
            print(f"Mirror directory \'{path}\' already exists")
        if not config_path.is_file():
            print(f"Creating config file \'{config_path}\'")
            configurer.new_config(config_path, self.root)
        else:
            print(f"Config file \'{config_path}\' already exists")
        if not db_path.is_file():
            print(f"Creating database \'{db_path}\'")
            filer.create_file(db_path)
        else:
            print(f"Database \'{db_path}\' already exists")

    def add(self, url: str, **kwargs) -> None:
        '''
        Adds the url to the mirror and downloads the video(s)
        '''

        # Config setup
        self.verify_config()
        self.load_config()

        # Load the options from config
        if not (active_options := self.load_options(kwargs)):
            print("Could not load options")
            return
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
        print(f"Adding \'{name}\' to the mirror")
        logging.info(f"Adding {url} to the mirror")
        self.config = configurer.set_yt(yt_string, id, self.config, specs)

        paths_table = databaser.open_table(self.db_path, "paths") # Need this to resolve collisions (only checking paths)

        # Local dicts before committing to db
        url_to_add = dict()                     # Wildcard url, could be channel, playlist or single 
        singles_to_add = dict()                 # Singles
        paths_to_add = dict()                   # Paths
        files_to_add = dict()                   # Files

        # Generate keys for the db
        keys = self.generate_keys(yt, dict(), active_options, paths_table)    # Get all the keys to add to the table
        url_to_add[url] = keys                                      # Mark the url for adding
        paths_to_add.update({ keys["path"]: {"parent": url} })      # Mark the path for adding
        logging.info(f"Adding {url} with keys {keys}")

        if "files" in keys:
            files = deepcopy(keys["files"])                         # Make a copy of the files
            files = self.init_files(files, url, active_options)     # Put some initial values
            files_to_add.update(files)                              # Mark the files for adding
            logging.info(f"Adding files {files}")

        # Handle children
        children = tuber.get_children(yt)
        if children:   # If the passed url has any children

            print(f'Found {len(children)} Youtube videos')
            parent_keys = {"parent": url, "parent_name": keys["name"], 
            "parent_type": yt_string, "path": keys["path"]}       # passing in parent info

            for child_url in children:

                yt = self.get_pytube(child_url, self.cache)                 # Get the pytube object
                child_keys = self.generate_keys(yt, parent_keys, active_options, paths_table) # Get the keys for the db
                name = child_keys['name']                                   # Get the name of the pytube object
                print(f'Adding \'{name}\'')
                singles_to_add[child_url] = child_keys                            # Mark it for adding
                # logging.info(f"Adding {child_url} with keys {child_keys}")

                files = deepcopy(child_keys["files"])                       # Make a copy of the files
                files = self.init_files(files, child_url, active_options)   # Put some initial values
                files_to_add.update(files)                                  # Mark the files for adding
                # logging.info(f"Adding files {files}")

                new_path = deepcopy(child_keys["path"])                     # Make a copy of the path
                paths_to_add.update({ new_path: {"parent": child_url} })    # Mark it for adding
                # logging.info(f"Adding path {new_path}")

        # Calculate download size
        if not kwargs.get("no_dl", False):
            download_size = self.calculate_download_size(files_to_add, active_options)

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
        configurer.save_config(self.config_path, self.config)

        # Open the database tables
        if yt_string in ['channel', 'playlist']:            # If it's a channel or playlist
            table = databaser.open_table(self.db_path, yt_string) # Get the appropriate database for the toplevel item
            table[url] = keys                               # Add it to the database
            table.commit()                                  # Commit the changes to the database
            table.close()
        else:
            singles_to_add[url] = keys  # Else, add it to the singles pile
        singles_table = databaser.open_table(self.db_path, "single")  # Where yt videos go
        files_table = databaser.open_table(self.db_path, "files")  # Where files go
        # Commit to database
        files_table.update(files_to_add)       # Record the files in the database
        paths_table.update(paths_to_add)       # Record the paths in the database
        singles_table.update(singles_to_add)   # Record all the singles
        files_table.close()            # Commit the changes to the database
        paths_table.close()            # Commit the changes to the database
        singles_table.close()          # Commit the changes to the database

        # Check if downloading is skipped
        if kwargs.get("no_dl", False):
            print("Skipping download")
            return
        
        if not kwargs.get("no_dl", False):
            self.sync(url=url, kwargs=kwargs)   # Sync all the files for this url

        print("Done!")

    def remove(self, url: str, **kwargs) -> None:
        """
        Removes the following url from the mirror and deletes the video(s)
        """

        # Localize our paths so we don't have to type self a bunch of times
        config_path = self.config_path

        print("Loading config")
        self.verify_config()
        self.load_config()
        
        # Parse the url & create pytube object
        try:
            yt_string = tuber.link_type(url)                # Get the url type (channel, playlist, single)
            id = tuber.link_id(url)                         # Get the id from the link
            yt = self.get_pytube(url, self.cache)           # Get the proper pytube object
            url = tuber.get_url(yt)                         # Need to get url from pytube in case user passed a dirty one
            name = tuber.get_name(yt)
        except Exception as e:
            logging.exception('Could not get info for url \'%s\' due to e', url, e)

        # Check if the id is already in the config
        if configurer.yt_exists(yt_string, id, self.config):
            print(f'Removing {yt_string} \'{name}\'')
            logging.info(f"Removing {url} from the mirror")
        else:
            print(f"{url} is not in the mirror")
            logging.info(f"Could not find {url} not found in the mirror")
            return

        # Get info from the db
        table = databaser.open_table(self.db_path, yt_string, autocommit=False)  # Open database
        keys = table[url]                                                        # Get the keys for the object
        remove_path = keys["path"]

        if not kwargs.get("no_rm", False):
            print("Calculating removal size...")
            path_size = self.calculate_path_size(remove_path)
            print(f"Removing will delete {printer.human_readable(path_size)} from the mirror")

        # Ask for confirmation
        if (not kwargs.get("force", False)) or not kwargs.get("no_rm", False):
            if input("Continue? (y/n) ") != "y":
                print("Aborting")
                return

        # Remove the directory
        if not kwargs.get("no_rm" ,False):
            print("Deleting files...")
            shutil.rmtree(remove_path, ignore_errors=True)  

        print("Getting paths to remove...")
        paths_to_remove = set()
        paths_to_remove.add(remove_path)
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
        if not (singles_table := self.get_table("single")):   # Get the singles table if not already initialized
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
        db_path = self.db_path
        files_table = databaser.open_table(db_path, "files", autocommit=False) # Get the files table
        paths_table = databaser.open_table(db_path, "paths", autocommit=False) # Get the paths table        

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
        
    def sync(self, url: str = None, **kwargs: dict) -> None:
        '''
        Syncs the mirror against the database
        '''

        # Localize our paths so we don't have to type self a bunch of times
        db_path = self.db_path

        # Load the config
        self.verify_config()
        self.load_config()

        if kwargs.get("update"):   # Update if specified
            self.update(url=url)

        # TODO Check for URL

        active_options = self.load_options(kwargs)


        files_table = databaser.open_table(db_path, "files") # Get the files table
        singles_table = databaser.open_table(db_path, "single") # Get the singles table 

        if url:                                         # If a url is specified, just sync that
            name = tuber.get_name(self.get_pytube(url, self.cache)) # Get name for pretty printing
            files_to_sync = dict()  
            yt_string = tuber.link_type(url)            # Get the type of link
            print(f"Syncing with {yt_string} {name}")

            if yt_string in ['channel', 'playlist']:
                table = databaser.open_table(db_path, yt_string)   # Open a table
                children = table[url]["children"]                  # Get the children from the db
                for child_url in children:
                    files = singles_table[child_url]["files"]      # Get the children files
                    for filepath in files:                  # Get the files from the files table
                        info = files_table[filepath]        # File dictionary
                        if not info["downloaded"]:          # If not downloaded
                            files_to_sync[filepath] = info      # Mark for syncing

            elif yt_string == 'single':
                    files = singles_table[url]["files"]     # Get the files from the db
                    for filepath in files:                  # Get the files from the files table
                        info = files_table[filepath]        # File dictionary
                        if not info["downloaded"]:          # If not downloaded
                            files_to_sync[filepath] = info      # Mark for syncing

            print(f'Syncing {len(files_to_sync)} files')
            for filepath in files_to_sync:
                file = files_to_sync[filepath]              # Get the file info
                filename = str(Path(filepath).name)         # Get just the filename for pretty printing
                parent = file["parent"]                     # Get the parent url
                file_type = file["type"]                    # Get the file type "video", "audio", etc. 
                yt = self.get_pytube(parent, self.cache)    # Get the pytube object   
                print(f"Downloading {file_type} {filename}")
                if (specs := downloader.download_single(yt, file_type, filepath, active_options)):
                    files_table.update({filepath:specs})     # Save the file specs to the database
                    files_table.commit()                    # Commit the changes to the database
                else:
                    print(f'Could not download {file_type} {filename}')
                
            print(f"Synced with \'{name}\'!")
            return url

        # If no url is specified, sync everything
        urls_to_sync = set()

        for yt_string in ['channel', 'playlist', 'single']:
            items = configurer.get_options(yt_string, self.config)
            for id in items:
                print(items[id]["url"])
                # urls_to_sync.add(item["url"])
            
        # print(urls_to_sync)

        print("All done!")
        return


    def update(
        self,
        url: str = None,
        ) -> None:
        '''
        Updates the database without downloading anything
        '''
        if not root:
            root = self.root

        # Localize our paths so we don't have to type self a bunch of times
        path = self.path
        config_path = self.config_path
        db_path = self.db_path

        if not config_path.is_file():                           # Verify the config file exists   
            logging.error(f'Could not find config file in root directory \'{path}\'')
            return
        if not db_path.is_file():                               # Verify the database file exists
            logging.error(f'Could not find database file in root directory \'{path}\'')
            return
        self.config = configurer.load_config(config_path)       # Load the config file

        channels = configurer.get_options("channel", self.config)   # Load channels
        playlists = configurer.get_options("playlist", self.config)   # Load channels

        channels_table = self.get_table("channel")   # Load channels table
        playlists_table = self.get_table("playlist") # Load playlists table

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
        return

    def verify(self) -> None:
        '''
        Verifies the integrity of the mirror (somehow)
        '''
        return

    def show(self) -> None:
        '''
        Prints the current state of the mirror
        '''

        # Localize our paths so we don't have to type self a bunch of times
        path = self.path
        config_path = self.config_path
        db_path = self.db_path

        self.config = configurer.load_config(config_path)       # Load the config file

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
            if url in cache:                    # If the url is already cached, return its object
                return cache[url]
            else:
                pytube = tuber.new_pytube(url)  # Get new pytube object
                cache[url] = pytube             # Cache it
                return pytube
        except Exception as e:
            logging.exception('Could not get pytube object for %s due to', url, e)
            return None

    def generate_keys(self, yt: Union[Channel, Playlist, YouTube], keys: dict, options: dict, paths: dict) -> dict:
        '''
        Generates the keys that we want to put into the database and returns as a dictionary.
        You can pass in a dict if you want to inject some values from above
        '''
        keys = deepcopy(keys)                     # Make a copy of the injected keys so they don't get altered
        yt_string = tuber.yt_to_type_string(yt)   # Get the type as a string
        metadata = tuber.get_metadata(yt)         # Strip the useful data off the pytube object
        keys.update(metadata)                     # Add to our keys
        yt_id = tuber.get_id(yt)                  # We use this to resolve collisions

        if yt_string in ["channel", "playlist"]:    # Do the same stuff for channels and playlists
            path = filer.calculate_path(yt_string, keys["name"], "")
            keys["path"] = filer.resolve_collision(path, paths, yt_id)
            return keys

        elif yt_string == "single":
            if "parent_name" not in keys:           # Check if the parent name is already in the keys
                keys["parent_name"] = "None"            # Parent's name is empty if it's a single

            if "parent_type" not in keys:           # Check if the parent type is already in the keys
                keys["parent_type"] = "single"      # Parent's type is single if it's a single
            else:
                yt_string = keys["parent_type"]     # We are resetting the type to the parent type

            if "path" not in keys:                  # If no path was passed, calculate a new one
                temp = filer.calculate_path(yt_string, "", keys["name"])
                keys["path"] = filer.resolve_collision(temp, paths, yt_id)
            else:   # Take the path and add the name
                name = safe_filename(keys["name"]).replace(' ', '_')
                temp = str(Path(keys["path"])/Path(name))
                keys["path"] = filer.resolve_collision(temp, paths, yt_id)
                
            keys["files"] = filer.get_files(keys["path"], keys["name"], options)  # Get the files for this video
            return keys
        else: 
            logging.error(f"Failed to get keys for {yt_string} {yt}")
            return None

    def init_files(self, files: dict, url: str, options: dict) -> dict:
        '''
        Takes files and fills in some default values
        '''
        for filepath in files:    # Add some extra info we only want in the files table
            file = files[filepath]
            file["parent"] = url
            file["downloaded"] = False
            if file["type"] == "video":
                file["resolution"] = options["resolution"]
            logging.debug((f'Updating file {filepath} with keys {file}'))
        return files

    def calculate_download_size(self, files: dict, options: dict) -> int:
        '''
        Calculates the total size of the files to be downloaded
        '''
        download_size = 0
        for filepath in files:
            file = files[filepath]               # Get the file info
            parent = file["parent"]                     # Get the parent url
            yt = self.get_pytube(parent, self.cache)    # Get the pytube object
            file_type = file["type"]                    # Get the file type "video", "audio", etc.    
            print(f"Calculating filesize for {file_type} {str(Path(filepath).name)}")
            filesize = downloader.calculate_filesize(yt, file_type, options)   # Get the filesize
            file["filesize"] = filesize                 # Record the filesize while we're here
            download_size += filesize                   # Add the filesize to the total download size
        return download_size

    def calculate_path_size(self, path):
        path_size = 0
        for root, dirs, files in os.walk(path, topdown=False):  # Find all the files in the directory
            for name in files:                                  # Search through all the files
                filepath = os.path.join(root, name)             # Get the filepath
                filepath = Path(filepath)
                path_size += filepath.stat().st_size
        return path_size

    def verify_config(self):
        '''
        Verifies all the files are available
        '''
        if not self.config_path.is_file():               # Verify the config file exists   
            logging.error(f'Could not find config file in directory \'{self.path}\'')
            return
        if not self.db_path.is_file():                   # Verify the database file exists
            logging.error(f'Could not find database file in directory \'{self.path}\'')
            return

    def load_config(self):
        try:
            self.config = configurer.load_config(self.config_path)
        except Exception as e:
            logging.exception(f"Could not load given config file due to {e}")
            return

    def load_options(self, **kwargs):
        '''
        Loads various options
        '''
        active_options = configurer.defaults                                # Load default options
        global_options = configurer.get_globals(self.config)                # Get global options
        active_options.update(global_options)                               # Overwrite with globals
        active_options.update(kwargs)                                       # Overwrite with command line options
        active_options["has_ffmpeg"] = shutil.which("ffmpeg") is not None   # Record whether they have ffmpeg
        if active_options["resolution"] not in downloader.resolutions:
            logging.error(f"Invalid resolution \'{active_options['resolution']}\', valid resolutions = {downloader.resolutions}")                                      # Validate resolution
            return None
        return active_options

