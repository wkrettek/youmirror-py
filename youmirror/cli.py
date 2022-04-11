__all__ = ['app', 'sync', 'add', 'remove', 'check', 'main', '__main__']

import typer
from typing import Optional, List

app = typer.Typer()

def main():
    app()

@app.command()
def sync(
    config_file : List[str] = typer.Argument(None),
    dry_run : Optional[bool] = typer.Option(False)
    ):
    '''
    Uses a config file to sync the file tree to Youtube's videos
    '''
    print('sync called')
    print(f'Dry run is {dry_run}')
    return

@app.command()
def add(
    dry_run: bool = False
    ):
    '''
    Adds the specified channel, playlist, or single to the config file and downloads
    '''
    print('add called')
    return

@app.command()
def remove():
    '''
    Removes the specified channel, playlist, or single from the config file and downloads
    '''
    print('remove called')
    return

@app.command()
def check():
    '''
    Checks the database to see if any mirrored files are no longer supported by Youtube
    '''
    print('check called')

if __name__ == "__main__":
    main()