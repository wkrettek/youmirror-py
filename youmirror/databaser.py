# This module creates a database and manages it
import sqlite3
import logging
import sys



def db_exists(dpath : str):
    '''
    Checks if the db exists
    '''
    pass

def connect_db(dbpath : str):
    try:
        conn = sqlite3.connect(dbpath)
    except Exception as e:
        logging.exception(f"Could not connect to database due to {e}")
        sys.exit()
    return conn

def load_db(dbpath : str):
    pass




db_params = {
    "url": "",
    "title": "",
    "author": "",
    "is_available": bool,
    "locked": True,

}