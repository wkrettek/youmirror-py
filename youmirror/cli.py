import logging

import typer

from youmirror.core import YouMirror

app = typer.Typer(
    help="Create a mirror of your favorite youtube videos", add_completion=True
)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    app()


def exit_on_failure(ok: bool) -> None:
    if not ok:
        raise typer.Exit(code=1)


@app.command()
def new(root: str = typer.Argument(".", help="The directory to create the mirror in")):
    """
    Create a new mirror in the given directory [default:'./']
    """
    YouMirror(root=root).new()


@app.command()
def add(
    url: str = typer.Argument(..., help="Specify the url to add"),
    mirror: str = typer.Option(
        "./", "-m", "--mirror", help="Specify the mirror directory"
    ),
    resolution: str | None = typer.Option(
        None, "--resolution", help="'best' (default) or a ceiling like '1080p'"
    ),
    name: str | None = typer.Option(
        None, "--name", help="Folder name for the source [default: its title]"
    ),
    no_dl: bool = typer.Option(
        False, "--no-dl", help="Adds the url to the mirror without downloading"
    ),
):
    """
    Adds the url to the mirror and downloads videos
    """
    exit_on_failure(YouMirror(root=mirror).add(url, resolution, name, no_dl))


@app.command()
def remove(
    url: str,
    mirror: str = typer.Option(
        "./", "-m", "--mirror", help="Mirror directory to remove from"
    ),
    delete: bool = typer.Option(
        False, "--delete", help="Also delete the downloaded files"
    ),
):
    """
    Stops tracking the url in the mirror
    """
    exit_on_failure(YouMirror(root=mirror).remove(url, delete))


@app.command()
def sync(
    url: str = typer.Argument(None, help="Specify the url to sync"),
    mirror: str = typer.Option(
        "./", "-m", "--mirror", help="The mirror directory to sync"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Shows what would download without downloading"
    ),
):
    """
    Checks for new videos and downloads everything not downloaded yet
    """
    exit_on_failure(YouMirror(root=mirror).sync(url, dry_run))


@app.command()
def show(
    mirror: str = typer.Option(
        ".", "-m", "--mirror", help="The mirror directory to show"
    ),
):
    """
    Shows the state of the mirror
    """
    exit_on_failure(YouMirror(root=mirror).show())


if __name__ == "__main__":
    main()
