from pytube import YouTube
from typing import Optional


def download_single(
    self, 
    url: str, 
    filename: Optional[str] = None, 
    output_path : Optional[str] = "", 
    is_channel: bool = False, 
    is_playlist : bool = False,
    playlist_title: str = ""
) -> None:
    '''
    Download a single video
    '''
    yt = YouTube(url)
    title = yt.title
    author = yt.author
    if not url:
        self.logger.error("No URL provided")
        return
    if not filename:
        filename = title + '.mp4'

    output_path += self.root    # Must have the root in the path
    if is_channel:              # Include author if the channel called us
        output_path += author 
    elif is_playlist:           # Include playlist title if the playlist called us
        output_path += playlist_title
    else:                       # Otherwise it's a single
        output_path += "singles/"
    
    # Download the video
    logging.info("Downloading %s to %s", url, output_path)
    try:
        yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(output_path=output_path, filename=filename)
    except FileNotFoundError:   # If the directory doesn't exist, create it
        logging.info(f"Creating directory {output_path}")
        os.makedirs(output_path, exist_ok=True)


def download_channel(self, url: str, filename: Optional[str]) -> None:
    '''
    Download all videos from a channel
    '''
    prefix = self.root + "channels/" + YouTube(url).channel_id
    # self.download_single(url=url, filename=filename, filename_prefix=)
    pass

def download_playlist(self) -> None:
    '''
    Download all videos from a playlist
    '''
    pass