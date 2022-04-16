__all__ = ['app', 'sync', 'add', 'remove', 'check', 'main', '__main__']

import typer
from typing import Optional
from youmirror.core import YouMirror

app = typer.Typer()

def main():

    app()

@app.command()
def sync(
    url : str,
    root : str = typer.Argument(None),
    dry_run : Optional[bool] = typer.Option(False)
    ):
    '''
    Syncs the filetree to the database
    '''
    print(f'Dry run is {dry_run}')
    return

@app.command()
def new(root : str = typer.Argument(None)):
    '''
    Create a new config file from the template
    '''
    ym = YouMirror()
    ym.new(root)
    return

@app.command()
def add(
    url : str,
    root : Optional[str] = typer.Argument(None, help='Root directory to add to'),
    # dl_off : Optional[bool] = typer.Option(False, help='Change the config file and database but do not download anything'),
    dry_run : Optional[bool] = typer.Option(default=False, help="Only calculate the changes")
    ):
    '''
    Adds the url to the mirror
    '''
    kwargs = {"dry_run": dry_run}
    yt = YouMirror()
    yt.add(url, root, **kwargs)
    return

@app.command()
def remove(
    url : str,
    root : Optional[str] = typer.Argument(None, help='Root directory to remove from'),
    ):
    '''
    Removes the specified link from the mirror and deletes all files
    '''
    ym = YouMirror()
    ym.remove(url, root)

@app.command()
def check():
    '''
    Checks the database to see if any mirrored files are no longer supported by Youtube.
    Generally updates metadata
    '''
    return

@app.command()
def update(root : str = typer.Argument(None)):
    '''
    Checks if new files were added to channels or playlists and downloads them
    '''
    return

@app.command()
def show(root: str = typer.Argument(None)):
    '''
    Shows the state of the mirror
    '''
    ym = YouMirror()
    ym.show(root)

@app.command()
def config(root: str = typer.Argument(None)):
    '''
    Allows you edit the config file
    '''
    pass  

@app.command()
def archive(root: str = typer.Argument(None)):
    '''
    Uploads the mirror to the internet archive
    '''
    pass

@app.command()
def play(root: str = typer.Argument(None)):
    '''
    Plays the video or something
    '''
    pass


if __name__ == "__main__":
    main()