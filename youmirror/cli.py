__all__ = ['app', 'sync', 'add', 'remove', 'check', 'update', 'main', '__main__']

import typer
from typing import Optional
from youmirror.core import YouMirror

app = typer.Typer(help="Create a mirror of your favorite youtube videos", add_completion=True)

def main():

    app()

@app.command()
def sync(
    url: str = typer.Argument(None, help="Specify the url to sync"),
    mirror: str = typer.Option('./', *('-m', '--mirror'), help="The mirror directory to sync"),
    update: bool = typer.Option(False, '--update', help="Update the database before syncing"),
    # dry_run : Optional[bool] = typer.Option(default=False, show_choices=False, help="Calculates changes with no execution"),
    ):
    '''
    Downloads videos to match the mirror
    '''
    kwargs = {"update": update}
    ym = YouMirror(root=mirror)
    ym.sync(url=url, **kwargs)
    return

@app.command()
def new(root : str = typer.Argument('.', help="The directory to create the mirror in")):
    '''
    Create a new mirror in the given directory [default:'./']
    '''
    ym = YouMirror(root=root)
    ym.new()
    return

@app.command()
def add(
    url : str = typer.Argument(None, help="Specify the url to add"),
    mirror : Optional[str] = typer.Option('./', *('-m', '--mirror'), help='Specify the mirror directory'),
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
    ym = YouMirror(root=mirror)
    ym.add(url, **kwargs)
    return

@app.command()
def remove(
    url : str,
    mirror : Optional[str] = typer.Option('./', *('-m', '--mirror'), help='Mirror directory to remove from'),
    no_rm : Optional[bool] = typer.Option(False, "--no-rm", help="Stop tracking without deleting any files")
    ):
    '''
    Removes the url from the mirror and deletes all files
    '''    
    kwargs = {"no_rm": no_rm}
    ym = YouMirror(root=mirror)
    ym.remove(url, **kwargs)

# @app.command()
# def check():
#     '''
#     Checks the database to see if any mirrored files are no longer supported by Youtube.
#     Generally updates metadata
#     '''
#     return

@app.command()
def update(
    url : str = typer.Argument(None, help="Specify the url to update"),
    mirror : Optional[str] = typer.Option('./', *('-m', '--mirror'), help='Root directory for the mirror'),
    sync : Optional[bool] = typer.Option(False, "--sync", help="Sync the database after updating"),
    ):
    '''
    Updates the mirror when new videos are available
    '''
    kwargs = {"sync": sync}
    ym = YouMirror(root=mirror)
    ym.update(url=url, **kwargs)


@app.command()
def show(
    mirror: str = typer.Option('.', *('-m', '--mirror'), help="The mirror directory to show")
    ):
    '''
    Shows the state of the mirror
    '''
    ym = YouMirror(root=mirror)
    ym.show()

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