#!/usr/bin/env python

import argparse
import os
import requests
import shutil
import time

from spotipy import util, client


def get_album_cover(*, currently_playing, current_album_uri, save_path, verbosity_count):
    """Return the current album uri.

    TODO: More docstrings here
    """
    # If nothing is playing, return none
    if currently_playing is None:
        return

    # If the URI is the same, return the URI
    if current_album_uri == currently_playing.get('item').get('album').get('uri'):
        return current_album_uri

    # Otherwise, save the image
    album_image = currently_playing.get('item').get('album').get('images')[0].get('url')

    r = requests.get(album_image, stream=True)
    r.raise_for_status()

    with open(save_path, 'wb') as fp:
        shutil.copyfileobj(r.raw, fp)

    print("saved image...")

    current_album_uri = currently_playing.get('item').get('album').get('uri')

    return current_album_uri


def main(*, save_path, update_seconds, verbosity):
    """Get album cover."""
    username = os.environ['SPOTIFY_USERNAME']
    client_id = os.environ['SPOTIFY_CLIENT_ID']
    client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

    current_album_uri = None

    if None in (username, client_id, client_secret):
        raise(CoverGetterException, "Could not get environment variables.")
        return -1

    while True:

        token = util.prompt_for_user_token(
            username,
            scope='user-read-playback-state',
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri='http://localhost/'
        )

        if token:
            sp_client = client.Spotify(auth=token)

            currently_playing = sp_client.currently_playing()
            current_album_uri = get_album_cover(currently_playing=currently_playing,
                                                current_album_uri=current_album_uri,
                                                save_path=save_path,
                                                verbosity=verbosity)

        time.sleep(update_seconds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grab your currently playing album cover.')
    parser.add_argument('-p', '--path', help='Location to save album art', default='output.png')
    parser.add_argument('-i', '--interval',
                        help='Time to wait between checks',
                        type=float,
                        default=5)
    parser.add_argument('-v', '--verbosity', action='store_true', default=0)

    args = parser.parse_args()

    main(save_path=args.path,
         update_seconds=args.interval,
         verbosity=args.verbosity)


class CoverGetterException(Exception):
    """Exception class for CoverGetter."""

    pass
