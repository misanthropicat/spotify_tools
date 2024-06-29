import functools
import json
from datetime import date
from multiprocessing.pool import ThreadPool
from typing import List, Union

import spotipy
from ytmusicapi import YTMusic


class Yt2SpMigrator:
    def __init__(self, headers_file: str, sp_config: str):
        self.ytmusic = YTMusic(headers_file)
        with open(sp_config, "r") as f:
            config = json.load(f)
        self.sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(**config))

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

    def save_track_ids_to_playlist(self, track_ids: List[str], name: str) -> str:
        user_id = self.sp.current_user()['id']
        playlist_id = self.get_sp_playlist_by_name(name)
        if not playlist_id:
            playlist_id = self.sp.user_playlist_create(user=user_id,
                                                       name=name,
                                                       public=False)['id']
            self.sp.playlist_add_items(playlist_id, track_ids)
            return playlist_id
        pl_items = self.sp.playlist_items(playlist_id)['items']
        playlist_content = [p['id'] for p in pl_items]
        to_add = [t for t in track_ids if t not in playlist_content]
        if len(to_add) > 0:
            self.sp.playlist_add_items(playlist_id, to_add)
        return playlist_id

    def get_sp_playlist_by_name(self, p_name: str) -> Union[str, None]:
        playlists = self.sp.current_user_playlists()['items']
        playlist_id = [p['id'] for p in playlists if p['name'] == p_name]
        if len(playlist_id) == 0:
            return None
        return playlist_id[0]

    def merge_playlists(self, playlist1_id: str, playlist2_id: str, p_name: str) -> str:
        playlist1 = self.sp.playlist_items(playlist1_id)['items']
        playlist2 = self.sp.playlist_items(playlist2_id)['items']
        with ThreadPool() as p:
            p1_ids = p.map(self._unpack_track, playlist1)
            p2_ids = p.map(self._unpack_track, playlist2)
        to_add = self._non_duplicated_append(p1_ids, p2_ids)
        new_list = self.save_track_ids_to_playlist(p1_ids, p_name)  # spotify allows adding max 100 tracks per request
        with ThreadPool() as p:
            p.map(functools.partial(self.sp.playlist_add_items, new_list), [[t] for t in to_add])
        return new_list


if __name__ == '__main__':
    migrator = Yt2SpMigrator("headers.json", "config.json")
    liked_tracks = migrator.like_yt_tracks_on_sp(migrator.get_yt_playlist_by_name('Your Likes'))
    yt_2020_tracks = migrator.get_yt_playlist_by_name('My 2020 Year in Review')
    track_ids = migrator._get_sp_track_ids(yt_2020_tracks)
    name = f'YT migration {date.today()}'
    top2020_playlist = migrator.save_track_ids_to_playlist(track_ids, name)
    sp_top = migrator.get_sp_playlist_by_name('Your Top Songs 2020')
    yt_top = migrator.get_sp_playlist_by_name(f'YT migration {date.today()}')
    united_2020 = migrator.merge_playlists(sp_top, yt_top, 'United 2020 top')
    assert len(migrator.sp.playlist_items(united_2020)['items']) > 100
