# This module creates a database and manages it
import sqlite3
from sqlite3 import Connection
from sqlitedict import SqliteDict
import logging
import sys
from urllib import parse



def db_exists(dpath : str):
    '''
    Checks if the db exists
    '''
    pass

def connect_db(dbpath : str) -> Connection:
    try:
        conn = sqlite3.connect(dbpath)
    except Exception as e:
        logging.exception(f"Could not connect to database due to {e}")
        sys.exit()
    return conn

def load_db(dbpath : str):
    pass

def check_entry(conn : Connection, url : str, table: str) -> bool:
    '''
    Checks if the url is in the database
    '''
    url = parse.quote_plus(url) # Encode to be safe for sqlite
    try:
        cursor = conn.cursor()      # Create a cursor
        cursor.execute(f"SELECT * FROM {table} ") # Execute the query
        value = cursor.fetchall() # Fetch the results
        print(value)
        if value: # If there is a valid result
            return True
        else:
            return False
    except Exception as e:
        logging.exception(f"Could not check entry {url} in table {table} due to {e}")
        return False

def add_entry(conn, url : str, table : str):
    '''
    Adds an entry to the database
    '''
    url = parse.quote_plus(url) # Encode to be safe for sqlite
    try:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO {table} (url) VALUES ({url})")
        logging.info(f"Added entry {url} to table {table}")
    except Exception as e:
        logging.exception(f"Could not add entry {url} to table {table} due to {e}")

def table_exists(conn, table : str):
    '''
    Checks if the table exists
    '''
    try:
        conn.execute(f"SELECT * FROM {table}")
        return True
    except Exception as e:
        logging.exception(f"Table {table} does not exist")
        return False

def create_table(conn, table : str):
    '''
    Creates a table
    '''
    try:
        conn.execute(f"CREATE TABLE {table} (url TEXT PRIMARY KEY)")
        logging.info(f"Created table {table}")
    except Exception as e:
        logging.exception(f"Could not create table {table} due to {e}")
        sys.exit()
    pass

db_params = {
    "url": "",
    "title": "",
    "author": "",
    "is_available": bool,
    "locked": True, # Prevents from overwriting and deleting

}