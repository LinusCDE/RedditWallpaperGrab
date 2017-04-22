#!/usr/bin/env python3
'''
RedditGrab - Downloads images from reddit to use as wallpaper slideshow.

Please specify either username + password
or a client-id + client-secret.
'''

# Code-Design:
# This code respects PEP 8 Conventions and uses snake_case for naming

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import os
import praw
import random
import signal
import sys
import urllib3
import wallpaper_tool

USER_AGENT = 'redditGrab-Python'
ARGS = None

# Currently downloading file. Path stored here to delete it when process interrupted
DOWNLOADING_FILE_PATH = None

SUPPORTED_IMAGE_EXTENSIONS = [
    'jpg',
    'jpeg',
    'png',
    'bmp',
    'gif',
    'tiff'
]

AVAILABLE_SUBMISSION_ORDERS = [
    'controversial',
    'gilded',
    'hot',
    'new',
    'rising',
    'top'
]


def cancelled(sigid, event):
    '''SIGINT caught; process gets terminated (e.g. user typed CTRL+C)'''
    if DOWNLOADING_FILE_PATH:
        os.remove(DOWNLOADING_FILE_PATH)
    print('Cancelled!')
    exit(1)


def supported(filename):
    '''Check if a file is supported'''
    sp = filename.split('.')
    if len(sp) < 2:
        return False
    extension = sp[-1].lower()
    return extension in SUPPORTED_IMAGE_EXTENSIONS


def format(path, image_format):
    '''Replace extension to a given one'''
    return str().join(path.split('.')[:-1]) + '.' + image_format


def convert_image(img_file, dest_file, resolution, allow_blur):
    '''Start conversion. Checks for problems'''
    failMessage = None  # Message if conversion failed

    try:
        # Start image conversion
        wallpaper_tool.create_wallpaper(img_file, dest_file, resolution, allow_blur, min_size=tuple(int(val) for val in ARGS.min_size.split('x')))
        # Remove TempFile
        os.remove(img_file)
    except wallpaper_tool.ImageTooSmallExecption:
        failMessage = 'Image too small!'
    except Exception:
        failMessage = 'Conversion failed.'

    if failMessage:
        print(failMessage, file=sys.stderr)
        # Deleting Images when failed
        if os.path.exists(img_file):
            os.remove(img_file)
        if os.path.exists(dest_file):
            os.remove(dest_file)


def download(url, dest):
    '''Download a file from given url to a file (dest)'''
    global DOWNLOADING_FILE_PATH

    # Removing https to avoid SSL-Warnings
    if 'https://' in url:
        url = url.replace('https://', 'http://')

    if ARGS.verbose:
        print('Downloading "%s" to "%s"...' % (url, dest))

    # Request and start download
    http = urllib3.PoolManager()
    response = http.request('GET', url, preload_content=False)
    destFile = open(dest, 'wb')
    DOWNLOADING_FILE_PATH = destFile.name

    # Download file
    for chunk in response.stream(1024*8):
        destFile.write(chunk)

    # Close connection
    destFile.close()
    response.release_conn()
    DOWNLOADING_FILE_PATH = None


def download_reddit_images():
    '''Download images from reddit. Options are read from the variable ARGS'''

    # Create Reddit-Instance
    reddit = praw.Reddit(
        client_id=ARGS.client_id,
        client_secret=ARGS.client_secret,
        user_agent=USER_AGENT,
        username=ARGS.username,
        password=ARGS.password)

    # (Try to) create defined given directory if not existing
    try:
        folder = ARGS.output_folder
        if not os.path.exists(folder) or not os.path.isdir(folder):
            os.makedirs(folder)
            if ARGS.verbose:
                print('Created folder \'%s\'!' % folder)
    except Exception:
        raise Exception('Could not create folder!')

    # Get Submissions
    if ARGS.verbose:
        print('Getting submissions...')

    # Subreddit_Function to get submissions in requested order
    subreddit_func = None
    # Get subreddit_func independent of praw-version
    if hasattr(reddit, 'get_subreddit'):  # For older versions of praw
        subreddit = reddit.get_subreddit(ARGS.subreddit)
        subreddit_func = getattr(subreddit, 'get_' + ARGS.submission_order)
    else:  # Never versions of praw
        subreddit = reddit.subreddit(ARGS.subreddit)
        subreddit_func = getattr(subreddit, ARGS.submission_order)

    # Loop through submissions
    for num, submission in enumerate(subreddit_func(limit=ARGS.limit)):

        # Print current submission-title
        print('[%d] %s' % ((num+1), submission.title))

        imageUrl = submission.url
        # Ignore if no url given
        if imageUrl is None or imageUrl == '':
            continue

        # Gather the filename out of url
        fileName = imageUrl.split('/')[-1]
        if '?' in fileName:
            fileName = fileName.split('?')[0]

        # Declare temporary destination
        tmpdest = ARGS.output_folder + os.sep
        tmpdest += fileName + '.temp.' + str(random.randint(0, 1000000))
        # Declare destination
        dest = folder + os.sep + format(fileName, ARGS.format)

        # Ignore if image was already downloaded
        if os.path.exists(dest):
            if ARGS.verbose:
                print('File \'%s\' already exists! Skipping...' % dest)
            continue

        # Cancel download if url does not end with supported extension
        if not supported(fileName):
            if ARGS.verbose:
                print('File \'%s\' is not an Image! Skipping...' % fileName)
            continue
        # Download file
        download(imageUrl, dest if ARGS.raw else tmpdest)
        if (not ARGS.raw) and ARGS.verbose:
            print('Convert image to Wallpaper...')
        # Convert file if allowed
        if not ARGS.raw:
            size = tuple(int(val) for val in ARGS.size.split('x'))
            convert_image(tmpdest, dest, size, not ARGS.no_blur)


def complain_and_exit(message):
    '''Print message in unix-style and exit with exit-code 1'''
    print('%s: %s' % (sys.argv[0], message), file=sys.stderr)
    exit(1)


def main():
    '''Handle cli arguments and start conversion'''
    global ARGS

    # Add SIGINT-Handler ( = CTRL+C )
    signal.signal(signal.SIGINT, cancelled)

    # -------------------------------------------------------------------------
    # Declaring Arguments

    # Allow line-breaks
    ap = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter)

    # Subreddit-name
    ap.add_argument('subreddit', help='Target subreddit-name')
    ap.add_argument('output_folder', help='Where to download images to')

    # Verbose
    ap.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        help='Increase Verbosity')

    # Client-Id
    ap.add_argument(
        '--client-id', default='', metavar='your_clientid',
        help='Used to auth with reddit. See above for more')

    # Client-Secret
    ap.add_argument(
        '--client-secret', default='', metavar='your_clientsecret',
        help='Used to auth with reddit. See above for more')

    # User-Name
    ap.add_argument(
        '-u', '--username', default='', metavar='your_username',
        help='Alternative way of authenticating with reddit')

    # Password
    ap.add_argument(
        '-p', '--password', default='', metavar='your_pw',
        help='Can be used together with --username\n'
        'If --username given but no password, it will be promted')

    # Submission-Order
    ap.add_argument(
        '--submission-order', default='hot', metavar='order',
        help='Which submission order to use. Available: ' +
        str(', ').join(AVAILABLE_SUBMISSION_ORDERS))

    # Limit
    ap.add_argument(
        '-n', '--limit', default=100, metavar='limit', type=int,
        help='Limit of submissions to check. Default is 100')

    # Size
    ap.add_argument(
        '-s', '--size', default='1920x1080', metavar='WIDTHxHEIGHT',
        help='Size of formatted images\n'
        'Should be the resolution of your monitor\n'
        'Default is 1920x1080 (FullHD-16:9)')

    # No-Blur
    ap.add_argument(
        '-B', '--no-blur', action='store_true', default=False,
        help='Disables Blur-Effect when your Size-Ratio can not be matched')

    # Save-Raw
    ap.add_argument(
        '-r', '--raw', action='store_true', default=False,
        help='''Do not format at all.
         If used, --format will be ignored''')

    # Format
    ap.add_argument(
        '-f', '--format', default='png', metavar='image_format',
        help='''Output-Format for wallpapers.
         This option will be ignored if --raw is used.
         Default and recommended is png.
         All supported formats: %s'''
        % str(', ').join(SUPPORTED_IMAGE_EXTENSIONS))

    # Min-Size
    ap.add_argument(
        '-m', '--min-size', default=None, metavar='WIDTHxHEIGHT',
        help='''Minimum Size to be allowed for using.
         Any lower resolutions will be skipped.''')

    # -------------------------------------------------------------------------

    # Parsing argments into global ARGS
    ARGS = ap.parse_args()

    # -------------------------------------------------------------------------
    # Validating Arguments

    # if client-id given but client-secret missing or vice versa
    if (ARGS.client_id == '') is not (ARGS.client_secret == ''):
        if ARGS.client_id == '':
            complain_and_exit(
                'If --client-secret is given, --client-id is also required')
        else:
            complain_and_exit(
                'If --client-id is given, --client-secret is also required')

    # if username given but password missing or vice versa
    if (ARGS.username == '') is not (ARGS.password == ''):
        if ARGS.username == '':
            complain_and_exit(
                'If --password is given, --username is also required')
        else:
            complain_and_exit(
                'If --username is given, --password is also required')

    # Validate whether user-credentials or client-data is given
    if not ARGS.client_id and not ARGS.username:
        complain_and_exit(
            '''An authentication for Reddit is needed to use this program.
            Either you auth with --username and --password as regular login
            or use a --client-id and a --client-secret which you can obtain
            from https://www.reddit.com/prefs/apps/ .'''.replace(2*' ', ''))

    # Validate --format
    ARGS.format = ARGS.format.lower()
    if ARGS.format not in SUPPORTED_IMAGE_EXTENSIONS:
        complain_and_exit(
            '''The image-format you provided (%s) is not supported
            Please use one of the following:
            %s''' % (ARGS.format, SUPPORTED_IMAGE_EXTENSIONS.join(', ')))

    # Validate --limit
    if ARGS.limit < 0:
        complain_and_exit('The --limit has to be greater than 0')

    # Validate --size
    if 'x' not in ARGS.size:
        complain_and_exit('Format for --size is WIDTHxHEIGHT')

    try:
        # Check if dims are two numbers; if not ValueError will be raised
        width, height = (int(val) for val in ARGS.size.split('x'))
        if width < 10 or height < 10:
            raise ValueError('Too small')
    except ValueError:
        complain_and_exit('--size does contain invalid dimensions')

    # Validate --min-size
    if 'x' not in ARGS.min_size:
        complain_and_exit('Format for --min-size is WIDTHxHEIGHT')

    try:
        # Check if dims are two numbers; if not ValueError will be raised
        width, height = (int(val) for val in ARGS.min_size.split('x'))
        if width < 00 or height < 0:
            raise ValueError('Size can not be negative')
    except ValueError:
        complain_and_exit('--min-size does contain invalid dimensions')

    # -------------------------------------------------------------------------

    # Start download
    try:
        download_reddit_images()
    except Exception as ex:
        complain_and_exit('Error: %s' % str(ex))

    # Exit point


if __name__ == '__main__':
    # Entry point
    main()
