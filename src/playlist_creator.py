import argparse

import os
import random

import spotipy
from datetime import date

scopes = 'playlist-modify-public playlist-modify-private user-top-read user-read-private'

class PlaylistCreator:
    def __init__(self, username=None):
        self.sp = spotipy.Spotify(
            auth_manager=spotipy.SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'],
                                              client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
                                              redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'],
                                              scope=scopes,
                                              show_dialog=True,
                                              open_browser=False,
                                              username=username)
        )

    def get_top_tracks(self, range: str, limit=50, offset=0, accumulated_results=None):
        if accumulated_results is None:
            accumulated_results = []

        batch_limit = min(50, limit)
        results = self.sp.current_user_top_tracks(time_range=range, limit=batch_limit, offset=offset)
        if not results or not results['items']:
            return accumulated_results

        accumulated_results.extend([i['id'] for i in results['items']])
        if len(results['items']) < batch_limit:
            return accumulated_results

        if limit > batch_limit:
            return self.get_top_tracks(range, limit - batch_limit, offset + batch_limit, accumulated_results)

        return accumulated_results

    def get_todays_top_playlist(self, username: str, playlist_name: str):
        top_playlist = self.get_playlist_by_name(username, playlist_name)
        if top_playlist:
            return top_playlist['name']
        return None

    def get_recommendations(self,
                            seed_artists=None,
                            seed_genres=None,
                            seed_tracks=None,
                            limit=50,
                            country=None):
        batch_limit = min(100, limit)
        results = self.sp.recommendations(seed_artists, seed_genres, seed_tracks, batch_limit, country)
        return results

    def create_playlist(self, name: str, description: str, track_ids_list: list):
        user_id = self.sp.me()['id']
        result = self.sp.user_playlist_create(user_id, name, description=description)
        if len(track_ids_list) > 100:
            for i in range(0, len(track_ids_list), 99):
                self.sp.playlist_add_items(result['id'], track_ids_list[i:min(len(track_ids_list), i+99)])
        else:
            self.sp.playlist_add_items(result['id'], track_ids_list)
        return result['name']

    def get_user_playlists(self, username: str):
        return self.sp.user_playlists(username)

    def get_playlist_by_name(self, username: str, playlist_name: str):
        playlists = self.get_user_playlists(username)
        playlist = [p for p in playlists['items'] if p['name'] == playlist_name]
        if not playlist:
            print(f"Couldn't find playlist {playlist_name} for user {username}")
            return None
        return playlist[0]

    def get_all_playlist_tracks(self, playlist_id: str):
        def _get_playlist_tracks(self, playlist_id, offset, accumulated_results=None):
            if accumulated_results is None:
                accumulated_results = []

            results = self.sp.playlist_items(playlist_id,
                                             offset=offset,
                                             fields='items.track.id,total,next',
                                             additional_types=['track'])
            if not results or not results['items']:
                return accumulated_results

            tracks_ids = [i['track']['id'] for i in results['items']]
            accumulated_results.extend(tracks_ids)
            if results['next']:
                return _get_playlist_tracks(self, results['total'], accumulated_results)
            return accumulated_results
                
        return _get_playlist_tracks(self, playlist_id, 0)

    def get_unique_tracks(self, playlist_1, playlist_2):
        pl1_tracks = self.get_all_playlist_tracks(playlist_1['id'])
        pl2_tracks = self.get_all_playlist_tracks(playlist_2['id'])
        common_tracks = [id for id in pl1_tracks if id in pl2_tracks]
        i = 0
        for id in common_tracks:
            if i % 2 == 0:
                pl1_tracks.remove(id)
            else:
                pl2_tracks.remove(id)
            i += 1
        return pl1_tracks, pl2_tracks

    def make_blend(self, friend: str, friends_playlist_name: str, my_playlist_name: str, limit: int):
        me = self.sp.me()['id']
        friends_playlist = self.get_playlist_by_name(friend, friends_playlist_name)
        my_playlist = self.get_playlist_by_name(me, my_playlist_name)
        friends_tracks, my_tracks = self.get_unique_tracks(friends_playlist, my_playlist)
        amount = min(len(friends_tracks), len(my_tracks))
        result_tracks = []
        for i in range(0, amount):
            result_tracks.append(friends_tracks[i])
            result_tracks.append(my_tracks[i])
        if len(result_tracks) < limit:
            recommendations = self.get_recommendations(seed_tracks=result_tracks[0:3],
                                                       limit=limit-len(result_tracks))
            tracks_ids = [t['id'] for t in recommendations['tracks']]
            result_tracks.extend(tracks_ids)
        result_playlist = self.create_playlist(f"blend_{str(date.today())}_{random.randint(0, 100)}",
                                               f"Generated by yt2sp based on {friend}'s {friends_playlist_name} and {me}'s {my_playlist_name}",
                                               result_tracks[0:limit])
        return result_playlist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command',
                        choices=['get_top', 'get_recommendations', 'blend_with_friend'])
    parser.add_argument('-u', '--username',
                        default=os.environ.get('USERNAME'),
                        help='User to be logged in as')
    parser.add_argument('-r', '--time_range',
                        default='short_term',
                        choices=['short_term', 'medium_term', 'long_term'],
                        help='Applicable for "get_top". Time range for picking top tracks')
    parser.add_argument('-l', '--limit',
                        default=50,
                        help='Amount of tracks to have in final playlist')
    parser.add_argument('-f', '--friend',
                        help='Applicable for "blend_with_friend". Username of the user blend with whom should be created')
    parser.add_argument('-fp', '--friends-playlist',
                        help='Applicable for "blend_with_friend". Name of friend playlist to blend with current user one')
    parser.add_argument('-mp', '--my-playlist',
                        help='Applicable for "blend_with_friend". Name of current user playlist to blend with friend one')
    args = parser.parse_args()
    playlist_creator = PlaylistCreator(args.username)
    top_tracks_ids = playlist_creator.get_top_tracks(args.time_range, int(args.limit))
    
    match args.command:
        case 'get_top':
            playlist_name = f"top_{args.time_range}_{str(date.today())}"
            top_playlist = playlist_creator.get_todays_top_playlist(playlist_creator.sp.me()['id'],
                                                                    playlist_name)
            if not top_playlist:
                top_playlist = playlist_creator.create_playlist(playlist_name,
                                                                f"Generated by yt2sp for {args.time_range}",
                                                                top_tracks_ids)
            print(top_playlist)
        case 'get_recommendations':
            seed_tracks = random.choices(top_tracks_ids, k=5)
            result = playlist_creator.get_recommendations(seed_tracks=seed_tracks,
                                                          limit=int(args.limit),
                                                          country='SE')
            tracks_ids = [t['id'] for t in result['tracks']]
            recommendations_playlist = playlist_creator.create_playlist(f"recommendations_{str(date.today())}",
                                                                        f"Generated by yt2sp based on 5 random tracks from my current {args.time_range} top",
                                                                        tracks_ids)
            
            print(recommendations_playlist)
        case 'blend_with_friend':
            blend_playlist = playlist_creator.make_blend(args.friend,
                                                         args.friends_playlist,
                                                         args.my_playlist,
                                                         int(args.limit))
            print(blend_playlist)


if __name__ == '__main__':
    main()
