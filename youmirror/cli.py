__all__ = ['app', 'sync', 'add', 'remove', 'check', 'main', '__main__']

import typer
from typing import Optional
from youmirror.core import YouMirror

app = typer.Typer(help="Create a mirror of your favorite youtube videos", add_completion=False)

def main():

    app()

@app.command()
def sync(
    url : str,
    root : str = typer.Argument(None, help="The root directory to sync to, default=\'./\'"),
    # dry_run : Optional[bool] = typer.Option(default=False, show_choices=False, help="Calculates changes with no execution"),
    # no_update :Optional[bool] = typer.Option(default=False, show_choices=False, help="Syncs the mirror without updating"),
    ):
    '''
    Checks for new videos and downloads them
    '''
    ym = YouMirror()
    ym.sync()
    return

@app.command()
def new(root : str = typer.Argument(None)):
    '''
    Create a new mirror in the given directory [default:'./']
    '''
    ym = YouMirror()
    ym.new(root)
    return

@app.command()
def add(
    url : str,
    root : Optional[str] = typer.Argument(default=None, help='Root directory for the mirror'),
    resolution : Optional[str] = typer.Option("720p", "--resolution", help='Preferred resolution to download'),
    captions: Optional[bool] = typer.Option(False, "--captions", show_default=True, help='Download captions if available'),
    no_video : Optional[bool] = typer.Option(False, "--no-video", show_default=True, help='Don\'t download video'),
    audio: Optional[bool] = typer.Option(False, "--audio", show_default=True, help='Download audio separately'),
    thumbnail: Optional[bool] = typer.Option(False, "--thumbnail", show_default=True, help='Download thumbnail'),
    force : Optional[bool] = typer.Option(False, "--force", help='Force download without asking confirmation'),
    dry_run : Optional[bool] = typer.Option(False, "--dry-run", help="Calculates changes with no execution"),
    no_dl : Optional[bool] = typer.Option(False, "--no-dl", help='Like dry-run, but adds the url to the mirror without downloading')
    ):
    '''
    Adds the url to the mirror and downloads videos
    '''
    kwargs = {"resolution": resolution, "dl_video": not no_video, "dl_captions": captions, "dl_audio": audio, "dl_thumbnail": thumbnail, "force": force, "dry_run": dry_run, "no_dl": no_dl}
    yt = YouMirror()
    yt.add(url, root, **kwargs)
    return

@app.command()
def remove(
    url : str,
    root : Optional[str] = typer.Argument(None, help='Root directory to remove from'),
    no_rm : Optional[bool] = typer.Option(False, "--no-rm", help="Stop tracking without deleting any files")
    ):
    '''
    Removes the url from the mirror and deletes all files
    '''    
    kwargs = {"no_rm": no_rm}
    ym = YouMirror()
    ym.remove(url, root, **kwargs)

# @app.command()
# def check():
#     '''
#     Checks the database to see if any mirrored files are no longer supported by Youtube.
#     Generally updates metadata
#     '''
#     return

@app.command()
def update(
    root : Optional[str] = typer.Argument(default=None, help='Root directory for the mirror'),
    ):
    '''
    Checks for new videos without downloading
    '''
    ym = YouMirror()
    ym.update(root)


@app.command()
def show(root: str = typer.Argument(None)):
    '''
    Shows the state of the mirror
    '''
    ym = YouMirror()
    ym.show(root)

# @app.command()
# def config(root: str = typer.Argument(None)):
#     '''
#     Allows you edit the config file
#     '''
#     pass  

# @app.command()
# def archive(root: str = typer.Argument(None)):
#     '''
#     Uploads the mirror to the internet archive
#     '''
#     pass

# @app.command()
# def play(root: str = typer.Argument(None)):
#     '''
#     Plays the video or something
#     '''
#     pass


if __name__ == "__main__":
    main()