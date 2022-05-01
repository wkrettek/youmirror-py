### core
    In sync and update we wanna get all the urls up front and work through the array, instead of doing it recursively
    keep tables open thoughout the instance?
    Generate Keys does some weird stuff that people might not understand

### printer
    Put stuff in justified columns
    When downloading, try to keep stuff on one line

### Visualization
    Need good ways to view what's in the database
        I guess show could be good for this
            But also developer focused stuff
        Maybe like an export function in core which just exports the database to a csv file?

### Databaser
    Maybe we actually do need to hold the tables open in the core throughout the entire ym existence?
        We just can't try and close them
        Seems like we need to leave autocommit on too

### Downloader
    Download is best effort but logic could maybe be simplified a bit
    Still getting xml errors when converting captions. I need to do this in-house
        Maybe xml captions could be a download option? idk
    Catch common issues like Too many requests error
    We can bypass age restrictions but it requires user to login. Long term goal

### Verifier
    Verify the config against the database
        Walk down from config to yt's to files
        Walk up from files to yt's to config
    Offer various resolutions to the user if an error is found

## Core -- track
    This will manually allow you to add files to the tracking for whatever reason, parent is determined by path?
        

            