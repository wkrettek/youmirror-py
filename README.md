# youmirror
Youmirror is an archiving tool built on pytube for creating and managing a mirror of your favorite youtube videos

## Installation

You can install from github by using

`pip install git+https://github.com/wkrettek/youmirror.git`

If you have `poetry` you can clone this repository and install with

`poetry install --no-dev`

youmirror is intended for python 3.9 and higher

## Description

There are a lot of sites out there that will let you paste a youtube link and download a youtube video relatively quickly. You can even use youtube-dl or pytube to download youtube videos relatively quickly. But writing a script to manage downloading and organizing of whole channels or playlists is time-consuming and one-offs don't really make a consistent management system. This library is designed to address that issue.

With youmirror and the accompanying CLI you can spin up an archive filetree and quickly download videos with a single link!

## CLI

You can easily interact with youmirror using the command line tool. Create a new mirror with the
`new` command.

`youmirror new [folder]`

You can add to your mirror by using the `add` command with a youtube link. Any youtube link. With almost all commands you can use the `-m` or `--mirror` option to specify the mirror directory. Otherwise the current directory will be used. You can use the `--no-dl` option if you would like to start tracking the link without downloading any files.

`youmirror add "https://www.youtube.com/watch?v=Pa_HT9vQiLw&t=4s" -m [folder] [OPTIONS]`

Conversely you can remove from the mirror with the `remove` command.

`youmirror remove "https://www.youtube.com/watch?v=Pa_HT9vQiLw&t=4s" -m [folder] [OPTIONS]`

You can view the current state of your mirror with the `show` command

`youmirror show -m [folder] [OPTIONS]`

youmirror also offers a `sync` command that will download all undownloaded videos tracked by the mirror. If your download gets interrupted, or you don't want to download all the videos at once, you can always continue with `youmirror sync`.  You can also specify the `--update` flag to check for new videos before syncing.

`youmirror sync -m [folder] [OPTIONS]`

If you add a channel or playlist to your mirror, you can always check for new videos with `youmirror update`. It will find new videos and track them in the mirror without downloading. You can also specify the `--sync` flag to sync after updating.

`youmirror update -m [folder] [OPTIONS]`

## Organization

youmirror does all the organization and filetree-building so you don't have to. Here is what the filetree looks like from a high level:

```
   Root
    | -- channels
            | -- channel name
                    | -- single name
                            | -- files
    | -- playlists
            | -- playlist name
                    | -- single name
                            | -- files
    | -- singles
            | -- single name
                    | -- files
```
            
You may notice that I use the term 'single' to refer to a single youtube video. This is leaning into the fact that there is a lot of information that can be downloaded from a youtube video, including downloading the audio separately, or downloading the captions. Also, singles are youtube videos that were added separately from a playlist or a channel.


## Downloading

youmirror offers best-effort downloading. This means youmirror will attempt to download the best quality stream that matches your request. By default, youmirror will download at 720p if available. If 720p is not available, it will download the next best resolution for the video. 

You can specify higher resolutions if you prefer, but Youtube does not serve higher res streams with combined audio, so if a higher resolution is specified, youmirror will find the highest quality audio stream and attempt to combine it with the video using `ffmpeg`. If you don't have `ffmpeg`, you can download it [here](https://www.ffmpeg.org/download.html). It's not required, so you can download videos at up to 720p without it.


## Configuration

Similar to poetry, youmirror uses a .toml config file to keep track of what's in your mirror. Tom's Obvious Minimal Language is designed to be a more human readable text system, as opposed to JSON or XML. So, if you ever want to, you can open the .toml file and get a pretty good idea of what is in your mirror.

```
[youmirror]
name = "new_mirror"
created_at = "2022-04-16"

[channel]

[playlist.PLBZw8Bdva63UAhbdAlbbYotegKhUMeSzN]
name = "Pepe Prawn"
url = "https://www.youtube.com/playlist?list=PLBZw8Bdva63UAhbdAlbbYotegKhUMeSzN"

[single.FWFQn6o4FfY]
name = "MIB3 - The Will Smith Slap"
url = "https://youtube.com/watch?v=FWFQn6o4FfY"

[single.1MbvNXZL5f0]
name = "Bill Hader in Men In Black 3"
url = "https://youtube.com/watch?v=1MbvNXZL5f0"
```

