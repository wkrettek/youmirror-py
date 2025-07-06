# youmirror
Youmirror is an archiving tool built on pytube for creating and managing a mirror of your favorite youtube videos

## Installation

You can install from github by using

`pip install git+https://github.com/wkrettek/youmirror.git`

If you have `uv` you can clone this repository and install with

`uv sync`

youmirror is intended for **python 3.11** and higher

## Description

So often you will make a playlist of your favorite videos, and as you return to it over the years, some videos will go private or be taken down due to copyright, and they will disappear forever. There are a lot of sites out there that will let you paste a youtube link and download a youtube video relatively quickly. But a lot of times those sites are riddled with ads, or don't offer downloads of high quality videos. There are python libraries out there that will let you download videos, but they just output to one directory by default, and that doesn't make a consistent management system. Or you might forget which videos you already have and you don't want to bother redownloading them. This library is designed to address that issue.

With youmirror and the accompanying CLI you can use any youtube link to add videos to your mirror and easily sync your filetree to what's on the web. Youmirror wil automatically spin up a filetree and organize files so you don't have to.  You can use youmirror to automatically check for new videos on playlists and channels and add them to your mirror. You can specify the quality of videos you want to download and youmirror will skip videos that are already downloaded. Once added, you can easily keep track of what is in your mirror.

## CLI

You can easily interact with youmirror using the command line tool. Create a new mirror with the `new` command.

`youmirror new [folder]`

You can add to your mirror by using the `add` command with a youtube link. Any youtube link. You can use the `--no-dl` option if you would like to start tracking the link without downloading any files. With almost all commands you can use the `-m` or `--mirror` option to specify the mirror directory. Otherwise the current directory will be used. 

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
            
You may notice that I use the term 'single' to refer to a single youtube video. This is leaning into the fact that there is a lot of information that can be downloaded from a youtube video, including downloading the audio separately, or downloading the captions. They will all be kept in the same folder for the single. By default, adding the url to the mirror will download the video, but you can use different flags like `--captions` when adding the url to also download captions.

## Downloading

youmirror offers best-effort downloading. This means youmirror will attempt to download the best quality stream that matches your request. By default, youmirror will download at 720p if available. If 720p is not available, it will download the next best resolution for the video. 

You can specify higher resolutions if you prefer, but Youtube does not serve higher res streams with combined audio, so if a higher resolution is specified, youmirror will find the highest quality audio stream and attempt to combine it with the video using `ffmpeg`. If you don't have `ffmpeg`, you can download it [here](https://www.ffmpeg.org/download.html). It's not required, so you can download videos at up to 720p without it.


## Configuration

Similar to poetry, youmirror uses a .toml config file to keep track of what's in your mirror. Tom's Obvious Minimal Language is designed to be a more human readable text system, as opposed to JSON or XML. So, if you ever want to, you can open the .toml file and get a pretty good idea of what is in your mirror.

```
[youmirror]
name = "new_mirror"
created_at = "2022-04-29"

[channel."http://www.youtube.com/c/suckerpinch"]
name = "suckerpinch"
last_updated = "2022-04-29"
resolution = "1080p"

[playlist."https://www.youtube.com/playlist?list=PLBZw8Bdva63UAhbdAlbbYotegKhUMeSzN"]
name = "Pepe Prawn"
last_updated = "2022-04-29"
resolution = "720p"

[single."https://youtube.com/watch?v=FWFQn6o4FfY"]
name = "MIB3 - The Will Smith Slap"
last_updated = "2022-04-29"
resolution = "720p"
```

