'''
This module creates a database and manages it
----
I've realized that the database is the most important thing in this whole project. 
Downloading the files should be super easy given a database. This means the database
must contain the information necessary to populate the filetree
db
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
        return SqliteDict(path, tablename=table, autocommit=True)   # TODO in the future I would like to 
    else:
        logging.debug(f"Invalid table {table} given")
        return None

def set_id(table: SqliteDict, id: str, value: dict) -> None:
    '''
    Sets a row in the given table
    '''
    table[id] = value

def get_id(table: SqliteDict, id: str) -> dict:
    '''
    Gets a row in the given table
    '''
    if  id in table:
        return table[id]
    else:
        logging.debug(f"Could not find id {id} in table {table}")
        return None

def set_files(table: SqliteDict, id: str, files: dict) -> dict:
    pass

def get_files(table: SqliteDict, id: str):
    pass


# def check_entry(conn : Connection, url : str, table: str) -> bool:
#     '''
#     Checks if the url is in the database
#     '''
#     url = parse.quote_plus(url) # Encode to be safe for sqlite
#     try:
#         cursor = conn.cursor()      # Create a cursor
#         cursor.execute(f"SELECT * FROM {table} ") # Execute the query
#         value = cursor.fetchall() # Fetch the results
#         print(value)
#         if value: # If there is a valid result
#             return True
#         else:
#             return False
#     except Exception as e:
#         logging.exception(f"Could not check entry {url} in table {table} due to {e}")
#         return False

# def add_entry(conn, url : str, table : str):
#     '''
#     Adds an entry to the database
#     '''
#     url = parse.quote_plus(url) # Encode to be safe for sqlite
#     try:
#         cur = conn.cursor()
#         cur.execute(f"INSERT INTO {table} (url) VALUES ({url})")
#         logging.info(f"Added entry {url} to table {table}")
#     except Exception as e:
#         logging.exception(f"Could not add entry {url} to table {table} due to {e}")

# def table_exists(conn, table : str):
#     '''
#     Checks if the table exists
#     '''
#     try:
#         conn.execute(f"SELECT * FROM {table}")
#         return True
#     except Exception as e:
#         logging.exception(f"Table {table} does not exist")
#         return False

# def create_table(conn, table : str):
#     '''
#     Creates a table
#     '''
#     try:
#         conn.execute(f"CREATE TABLE {table} (url TEXT PRIMARY KEY)")
#         logging.info(f"Created table {table}")
#     except Exception as e:
#         logging.exception(f"Could not create table {table} due to {e}")
#         sys.exit()
#     pass