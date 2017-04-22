RedditWallpaperGrab
===================

## Description

This tool can download images from any given subreddit. It already works quite well, but there are still a lot of things to do.

I created this tool to view the images from certain subreddits and use them as wallpaper slideshow on my computer.

Some subreddits I personally recommend for Wallpapers:
- [/r/wallpapers](https://www.reddit.com/r/wallpapers/)
- [r/EarthPorn](https://www.reddit.com/r/EarthPorn/)

## Features and Goals

### Features / Done:
- [x] Authentificate with the Reddit-API (via praw) using
  - username and password
  - client-id and client-secret see [Apps in your Reddit-Settings](https://www.reddit.com/prefs/apps/) for more
- [x] Download images from specfied subreddits
- [x] Convert images
  - Downscale to specfied resolution
  - Add a [SquareFit-Like effect](http://imgur.com/a/phBhY) to fit image ratio
- [x] Configurable with command line arguments

### Upcoming:
- [x] Setting a minimum resolution or use desktop resolution to prevent unsharp wallpapers
- [ ] Better filenames
- [ ] Support for praw 4.4.0

### Goals for the future:
- [ ] Automatic Resolution-Detection with cossplatform and multi monitor support (Currently defaults to FullHD)
- [ ] Add creds for the creators of the images in a stylish way
- [ ] OAuth2 with praw ([Source](https://praw.readthedocs.io/en/v3.6.0/pages/oauth.html))
- [ ] Make this into a pip package
- [ ] Polish this README

## Installation

To use this you'll need following dependencies

### Dependencies
- Python 3 or higher
- [praw 3.6.1](https://pypi.python.org/pypi/praw/3.6.1) (4.4.0 support is planned)
- [argparse](https://docs.python.org/3/library/argparse.html)
- [ Pillow / PIL ](https://github.com/python-pillow/Pillow)

All sources should be available throuh pip3. Please keep in mind to use **praw 3.6.1** newer versions will probably fail

### Installation steps

#### On Linux

Install *git*, *python3* and *pip3* with package manager of your distro. You may have those already on your system.

    $ cd ~ # Or any folder you want
    $ pip3 install argparse praw==3.6.1 pillow
    $ git clone https://github.com/LinusCDE98/RedditWallpaperGrab.git
    $ cd RedditWallpaperGrab
    $ chmod +x reddit_grab.py
    $ ./reddit_grab.py

#### On OS X

Should be the same as on Linux. I personally never had a Apple Device. As package manager you can use [Brew](https://brew.sh).

#### On Windows

- You need to install the latest Release of [Python 3](https://www.python.org/downloads/windows/) which should already ship with pip.
- Then you should be able to do pretty much the same as for Linux with the [Git Bash for Windows](https://git-for-windows.github.io/).

I personally do not have a Windows PC. You may need to search in the Internet for how to get the dependencies working in Windows.

***
If someone did the installation on OS X or Windows, I would appreciate your help to complete the according install steps.
