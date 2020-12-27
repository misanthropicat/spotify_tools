# yt2sp
This is a set of tools for user libraty migration from YT music to Spotify.

For successful using of this script you should create headers.json by the following steps:
1) authenticate in Youtube music
2) get headers from authenticated Youtube music GET requests
3) place the following headers to headers.json:
  - Authorization
  - Cookie
  - x-origin
  For a full information please read the documentation: https://ytmusicapi.readthedocs.io/en/latest/setup.html
    
And also you should create Spotify config.json with the following keys:
- client_id
- client_secret
- redirect_uri: you can use http://localhost:8888/callback for local script execution
- scope: as space-separated string. This script requires the followings:
  user-library-modify user-library-read playlist-read-private playlist-modify-private user-top-read user-read-email user-read-private
  For a full information please read the documentation: https://developer.spotify.com/documentation/general/guides/app-settings/, https://developer.spotify.com/documentation/general/guides/scopes/
