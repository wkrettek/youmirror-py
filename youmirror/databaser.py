'''
This module creates a database and manages it
# TODO 
I'm not a big fan of sqlite for this and I'd be happy to use something heavier. If I can find a good solution I will likely use that instead.
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
        return SqliteDict(path, tablename=table, autocommit=True)   # Set autocommits to be true for now for convenience
    else:
        logging.debug(f"Invalid table {table} given")
        return None

def set_key(db: SqliteDict, key: str, value: dict) -> None:
    '''
    Sets a row in the given database
    '''
    db[key] = value


# def connect_db(dbpath : str) -> Connection:
#     try:
#         conn = sqlite3.connect(dbpath)
#     except Exception as e:
#         logging.exception(f"Could not connect to database due to {e}")
#         sys.exit()
#     return conn


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