### VERSION 0.5.0 (All the stuff we need to do for first release)
    Double check that update does the same thing as add

### core
    **The local config for each url needs to persist between syncs (url's config gets loaded when it syncs)**
    Generate Keys does some weird stuff that people might not understand

### printer
    Figure out how to put stuff in columns
    Add Color
    [1] show name, type, url, num children, size

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
        

            