'''
This module creates a database and manages it
----
I've realized that the database is the most important thing in this whole project. 
With the database, you should be able to rebuild the whole filetree.
This means it should contain data from both the config file and filetree
db
| -- youmirror
        | -- key: primary key (can be whatever)
        | -- List[configs] the rest of the keys are the configs
| -- channels
        | -- id:        primary key (comes from channel_uri)
        | -- children:  id (primary key for singles)
        | -- config:    options dict from config (examples: "resolution" "locked", "extension") 

| -- playlists
        | -- id:        primary key
        | -- children:  id (primary key for singles)
        | -- config:    options dict from config (examples: "resolution" "locked", "extension") 
| -- singles
        | -- id:        primary key
        | -- type:      ("channel", "playlist" or "single")
        | -- parent_id: id (primary key for either a channel or playlist or none)
        | -- parent_name: name of the parent
        | -- config:    options dict from config (this will match whatever the parent has if there is one)
        | -- files:     dictionary that tracks all the files we have # TODO in the future, may make the filenames lists of strings so you can download multiple types, for now let's keep one
                | --    example: ("video": "/videos/singles/video_name.mp4)
                | --    example: ("audio": "/videos/singles/video_name.mp3)
                | --    example: ("caption": "/videos/singles/video_name.srt)
                | --    example: ("thumbnail": "/videos/singles/video_name.jpg)
| --  filetree  We need this to detect collisions, primary key is a path/file
# TODO 
I'm not a big fan of sqlite for this and I'd be happy to use something heavier if it's more robust. If I can find a good solution I will likely use that instead.
I need to abstract the database management as much as possible so it's easy to swap out.
The earlier we can find the best database the better, 
because changing databases later on will fuck everybody's archives all up
'''
from sqlitedict import SqliteDict
import logging
from pathlib import Path

db_file = "youmirror.db"

def get_table(path: Path, table: str) -> SqliteDict:
    '''
    Returns a table from the database that matches the string
    '''
    valid_tables = {"channels", "playlists", "singles"}
    if table in valid_tables:
        return SqliteDict(path, tablename=table, autocommit=True)   # TODO in the future I would like to wait to commit all at once, but I get concurrency errors without it
    else:
        logging.debug(f"Invalid table {table} given")
        return None

def set_id(table: SqliteDict, id: str, value: dict) -> None:
    '''
    Sets a row in the given table by id
    '''
    table[id] = value

def get_id(table: SqliteDict, id: str) -> dict:
    '''
    Gets a row in the given table by id
    '''
    if  id in table:
        return table[id]
    else:
        logging.debug(f"Could not find id {id} in table {table}")
        return {}

def set_key(table: SqliteDict, id: str, key: str, value: str) -> str:
    '''
    Sets the value of the key for the given id
    '''
    try:
        row = get_id(table, id) # Get the row by id
        row[key] = value
        set_id(table, id, row)
        return value
    except Exception as e:
        logging.exception(f"Could not set key {key} to value {value} due to {e}")

def get_key(table: SqliteDict, id: str, key: str) -> str:
    '''
    Gets the value of the key for the given id
    '''
    try:
        row = get_id(table, id) # Get the row by id
        if key in row:
            value = row[key]
            return value
        else:
            logging.debug(f"Could not find key {key} for id {id} in table {table.tablename}")
            return ""
    except Exception as e:
        logging.exception(f"Could not set key {key} in id {id} due to {e}")
        return None

def add_yt(table: SqliteDict, filetree: SqliteDict, yt_string: str, id: str, keys: dict, ) -> None:
    '''
    Adds the yt and its info to the database
    '''
    pass

def remove_yt(table: SqliteDict, filetree: SqliteDict):
    '''
    Removes the yt and its info from the database
    '''
    pass


def set_files(table: SqliteDict, id: str, files: dict) -> dict:
    '''
    Sets the files dictionary in the id and returns the files that were set
    
    '''
    valid_tables = {"singles"}    # Valid tables that you can set files in
    if table.tablename in valid_tables:
        try:
            row = get_id(table, id) # Retrieve the row
            row["files"] = files
            set_id(table, id, row)
            return files
        except Exception as e:
            logging.exception(f"Could not set files {files} in the table {table.tablename} due to {e}")
            return None
    else:
        logging.error(f'Could not set files in invalid table {table.tablename}')
        return None

def get_files(table: SqliteDict, id: str) -> dict:
    '''
    Gets the files dictionary from the id in the given table
    '''
    valid_tables = {"singles"}    # Valid tables that you can request files from
    if table.tablename in valid_tables:
        try:
            row = get_id(table, id)
            if "files" in row:
                files = row["files"]
                return files
        except Exception as e:
            logging.exception(f'Could not get files from table {table.tablename} with id {id} due to {e}')
            return None
    else:
        logging.error(f'Could not retrieve files from invalid table {table.tablename}')
        return None

def set_config(table: SqliteDict, id: str, config: dict) -> dict:
    '''
    Sets the config dictionary in the id and returns the config that was set    
    '''
    valid_tables = {"channels", "playlists", "singles"}    # Valid tables that you can set the config in
    if table.tablename in valid_tables:
        try:
            row = get_id(table, id) # Retrieve the row
            row["config"] = config
            set_id(table, id, row)
            return config
        except Exception as e:
            logging.exception(f"Could not set config {config} in the table {table.tablename} due to {e}")
            return None
    else:
        logging.error(f'Could not set config in invalid table {table.tablename}')
        return None


def get_config(table: SqliteDict, id: str) -> dict:
    valid_tables = {"channels", "playlists", "singles"}    # Valid tables that you can set the config in
    if table.tablename in valid_tables:
        try:
            row = get_id(table, id)
            if "config" in row:
                config = row["files"]
                return config
        except Exception as e:
            logging.exception(f'Could not get files from table {table.tablename} with id {id} due to {e}')
            return None
    else:
        logging.error(f'Could not retrieve files from invalid table {table.tablename}')
        return None