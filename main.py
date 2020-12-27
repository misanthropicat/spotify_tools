import functools
import json
from datetime import date
from multiprocessing.pool import ThreadPool
from typing import List, Union

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic


class Yt2SpMigrator:
    def __init__(self, headers_file: str, sp_config: str):
        self.ytmusic = YTMusic(headers_file)
        with open(sp_config, "r") as f:
            config = json.load(f)
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(**config))

    def _unpack_search_result(self, result: dict) -> Union[str, None]:
        tracks = result['tracks']['items']
        return tracks[0]['id'] if len(tracks) > 0 else None

    def _unpack_track(self, result: dict) -> str:
        return result['track']['id']

    def _get_sp_track_ids(self, yt_playlist: List[dict]) -> list:
        track_maps = [dict(artist=t['artists'][0]['name'], track=t['title']) for t in yt_playlist]
        queries = [f'track:{t["track"]} artist:{t["artist"]}' for t in track_maps]
        with ThreadPool() as p:
            results = p.map(functools.partial(self.sp.search, type='track'), queries)
            track_list = p.map(self._unpack_search_result, results)
        while None in track_list:
            track_list.remove(None)
        return track_list

    def _non_duplicated_append(self, list1: List[str], list2: List[str]) -> list:
        in_first = set(list1)
        in_second = set(list2)
        in_second_but_not_in_first = in_second - in_first
        return list(in_second_but_not_in_first)

    def get_yt_playlist_by_name(self, playlist_name: str) -> list:
        library = self.ytmusic.get_library_playlists()
        playlist_id = [p['playlistId'] for p in library if p['title'] == playlist_name][0]
        return self.ytmusic.get_playlist(playlist_id, 200)['tracks']

    def _get_sp_liked_tracks(self):
        liked_tracks = self.sp.current_user_saved_tracks(limit=50)
        result_list = liked_tracks['items']
        i = 1
        while liked_tracks['next']:
            liked_tracks = self.sp.current_user_saved_tracks(limit=50, offset=50 * i)
            result_list.extend(liked_tracks['items'])
            i += 1
        return result_list

    def like_yt_tracks_on_sp(self, yt_playlist: list) -> list:
        track_ids_to_add = self._get_sp_track_ids(yt_playlist)
        liked_tracks = self._get_sp_liked_tracks()
        with ThreadPool() as p:
            liked_ids = p.map(self._unpack_track, liked_tracks)
            track_ids = self._non_duplicated_append(liked_ids, track_ids_to_add)
            # spotipy module takes track_id as list and spotify itself has a 50 tracks per request restriction.
            # It seems better to use multi-threading.
            p.map(self.sp.current_user_saved_tracks_add, [[t] for t in track_ids])
        after_adding = self._get_sp_liked_tracks()
        assert len(after_adding) > len(liked_tracks)
        return after_adding

    def migrate_yt_playlist_to_sp(self, yt_playlist: list):
        track_list = self._get_sp_track_ids(yt_playlist)
        user_id = self.sp.current_user()['id']
        playlist_id = self.sp.user_playlist_create(user=user_id, name=f'YT migration {date.today()}', public=False)[
            'id']
        return self.sp.playlist_add_items(playlist_id, track_list)


if __name__ == '__main__':
    """
    For successful using of this script you should do the following:
    1) authenticate in Youtube music
    2) get headers from authenticated Youtube music GET requests
    3) place the following headers to headers.json:
        - Authorization
        - Cookie
        - x-origin
    For a full information please read the documentation:
        https://ytmusicapi.readthedocs.io/en/latest/setup.html
    
    And also you should create Spotify config.json with the following keys:
    - client_id
    - client_secret
    - redirect_uri: you can use http://localhost:8888/callback for local script execution
    - scope: as space-separated string. This script requires the followings:
        user-library-modify user-library-read playlist-read-private playlist-modify-private user-top-read 
        user-read-email user-read-private
    For a full information please read the documentation: 
        https://developer.spotify.com/documentation/general/guides/app-settings/
        https://developer.spotify.com/documentation/general/guides/scopes/
    """
    migrator = Yt2SpMigrator("headers.json", "config.json")
    playlist_names = ['My 2020 Year in Review', 'Your Likes']
    liked_tracks = migrator.like_yt_tracks_on_sp(migrator.get_yt_playlist_by_name('Your Likes'))
    top2020_playlist = migrator.migrate_yt_playlist_to_sp(migrator.get_yt_playlist_by_name('My 2020 Year in Review'))
