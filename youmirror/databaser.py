'''
This module creates a database and manages it
----
I've realized that the database is the most important thing in this whole project. 
With the database, you should be able to rebuild the whole filetree.
This means it should contain data from both the config file and filetree
----
db
| -- channels
        | -- url        primary key
        | -- id:        extracted from url
        | -- children:  urls (primary key for singles)
        | -- config:    options dict from config (examples: "resolution" "locked") 
        | -- path:      path "channels/channel_name"

| -- playlists
        | -- url        primary key
        | -- id:        extracted from url
        | -- children:  url (primary key for singles)
        | -- config:    options dict from config (examples: "resolution" "locked") 
        | -- path:      path "playlists/playlist_name"
| -- singles
        | -- url:       url for the single
        | -- id:        primary key 
        | -- type:      ("channel", "playlist" or "single")
        | -- parent:    url for parent (primary key for either a channel or playlist or none)
        | -- parent_name: name of the parent
        | -- config:    options dict from config (this will match whatever the parent has if there is one)
        | -- files
                | --    filepath:        primary key
                            | -- type:          "video", "audio", "caption", "thumbnail"     
                            | -- caption_type:  "en", "a.en"            # TODO this should probably be language
                            | -- resolution:    "480p", "720p", "1080p" Just for videos
| --- paths
        | -- name:      path name "singles/single_name/", "channels/channel_name"
        | -- parent     url of parent channel or playlist or single
        | -- size:      total size of files inside
| --- files:            dictionary that tracks all the files we have
        | -- filepath:  primary key, Ex: "singles/single_name/single_name.mp4"
        | -- parent:    url of parent single
        | -- type:      file type: "video", "audio", "caption", "thumbnail"
        | -- language:  "en, a.en, fr"
        | -- resolution:"1080p", "720p" etc
        | -- bitrate    Audio bitrate
        | -- downloaded: True/False
        | -- size:      file size

I need to abstract the database management as much as possible so it's easy to swap out.
If a better databasing system comes along I will use that instead, but for now sqlitedict is fine.
'''
from copy import deepcopy
from sqlitedict import SqliteDict
import logging
from pathlib import Path

db_file = "youmirror.db"
valid_tables = {"channel", "playlist", "single", "paths", "files"}

def open_table(path: Path, table_name: str, autocommit=True) -> SqliteDict:
    '''
    Returns a table from the database that matches the string
    '''
    if table_name in valid_tables:
        return SqliteDict(path, tablename=table_name, autocommit=autocommit)
    else:
        logging.error(f"Invalid table {table_name} given")
        return None

def close_table(table: SqliteDict) -> bool:
    '''
    Closes the table and returns if successful
    '''
    try:
        table.close()
        return True
    except Exception as e:
        logging.exception('Could not close table %s due to %s', table.tablename, e)

def commit_table(table: SqliteDict) -> bool:
    '''
    Commits the table and returns if successful
    '''
    try:
        table.commit()
        return True
    except Exception as e:
        logging.exception('Could not commit table %s due to %s', table.tablename, e)

def set_entry(id: str, keys: dict, table: SqliteDict) -> str:
    '''
    Sets an item in the given database table
    '''
    try:
        table[id] = keys
        return id
    except Exception as e:
        logging.error("Could not add id %s to table %s", id, table.tablename)

def get_entry(id: str, table: SqliteDict) -> dict:
    '''
    If the id exists in the table, returns the matching entry as a dict
    '''
    if id in table:
        entry = deepcopy(table[id])
        return entry
    else:
        logging.error("Could not find entry for %s in table %s", id, table.tablename)

def remove_entry(id: str, table: SqliteDict) -> bool:
    '''
    Removes the entry from the table if it exists and returns if successful
    '''
    try:
        if id in table:
            del table[id]
        return True
    except Exception as e:
        logging.exception("Could not remove %s from table %s due to %s", id, table.tablename, e)
        return False


# def add_yt(table: SqliteDict, filetree: SqliteDict, yt_string: str, id: str, keys: dict, ) -> None:
#     '''
#     Adds the yt and its info to the database
#     '''
#     pass

# def remove_yt(table: SqliteDict, filetree: SqliteDict):
#     '''
#     Removes the yt and its info from the database
#     '''
#     pass

# def set_files(table: SqliteDict, id: str, files: dict) -> dict:
#     '''
#     Sets the files dictionary in the id and returns the files that were set
    
#     '''
#     valid_tables = {"singles"}    # Valid tables that you can set files in
#     if table.tablename in valid_tables:
#         try:
#             row = get_id(table, id) # Retrieve the row
#             row["files"] = files
#             set_id(table, id, row)
#             return files
#         except Exception as e:
#             logging.exception(f"Could not set files {files} in the table {table.tablename} due to {e}")
#             return None
#     else:
#         logging.error(f'Could not set files in invalid table {table.tablename}')
#         return None

# def get_files(table: SqliteDict, id: str) -> dict:
#     '''
#     Gets the files dictionary from the id in the given table
#     '''
#     valid_tables = {"singles"}    # Valid tables that you can request files from
#     if table.tablename in valid_tables:
#         try:
#             row = get_id(table, id)
#             if "files" in row:
#                 files = row["files"]
#                 return files
#         except Exception as e:
#             logging.exception(f'Could not get files from table {table.tablename} with id {id} due to {e}')
#             return None
#     else:
#         logging.error(f'Could not retrieve files from invalid table {table.tablename}')
#         return None

# def set_config(table: SqliteDict, id: str, config: dict) -> dict:
#     '''
#     Sets the config dictionary in the id and returns the config that was set    
#     '''
#     valid_tables = {"channels", "playlists", "singles"}    # Valid tables that you can set the config in
#     if table.tablename in valid_tables:
#         try:
#             row = get_id(table, id) # Retrieve the row
#             row["config"] = config
#             set_id(table, id, row)
#             return config
#         except Exception as e:
#             logging.exception(f"Could not set config {config} in the table {table.tablename} due to {e}")
#             return None
#     else:
#         logging.error(f'Could not set config in invalid table {table.tablename}')
#         return None


# def get_config(table: SqliteDict, id: str) -> dict:
#     valid_tables = {"channels", "playlists", "singles"}    # Valid tables that you can set the config in
#     if table.tablename in valid_tables:
#         try:
#             row = get_id(table, id)
#             if "config" in row:
#                 config = row["files"]
#                 return config
#         except Exception as e:
#             logging.exception(f'Could not get files from table {table.tablename} with id {id} due to {e}')
#             return None
#     else:
#         logging.error(f'Could not retrieve files from invalid table {table.tablename}')
#         return None