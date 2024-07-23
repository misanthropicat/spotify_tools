class PlaylistCreatorError(Exception):
    def __init__(
        self,
        message,
        username,
        command,
        time_range,
        playlist_name=None,
        friend=None,
        friends_playlist=None,
    ):
        super().__init__(message)
        self.username = username
        self.command = command
        self.time_range = time_range
        self.playlist_name = playlist_name
        self.friend = friend
        self.friends_playlist = friends_playlist


class UserInputError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)
