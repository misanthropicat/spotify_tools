import os
import random
from datetime import date

import kivymd.icon_definitions  # noqa
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.appbar.appbar import (
    MDActionTopAppBarButton,
    MDTopAppBar,
    MDTopAppBarLeadingButtonContainer,
    MDTopAppBarTitle,
    MDTopAppBarTrailingButtonContainer,
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText, MDIconButton
from kivymd.uix.fitimage import FitImage
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar.snackbar import (
    MDSnackbar,
    MDSnackbarActionButton,
    MDSnackbarActionButtonText,
    MDSnackbarButtonContainer,
    MDSnackbarSupportingText,
    MDSnackbarText,
)
from kivymd.uix.textfield import MDTextField

if platform == "android":
    from exceptions import PlaylistCreatorError, UserInputError
    from utils import download_from_url
else:
    from src.exceptions import PlaylistCreatorError, UserInputError
    from src.utils import download_from_url

__all__ = [
    "PlaylistCreatorLabel",
    "PlaylistCreatorTextButton",
    "PlaylistCreatorSnackbar",
    "MainScreen",
]


class PlaylistCreatorLabel(MDLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.font_style = "Body"
        self.role = "large"
        self.valign = "center"


class PlaylistCreatorTextButton(MDButton):
    def __init__(self, *args, **kwargs):
        text = kwargs["text"]
        del kwargs["text"]
        super().__init__(
            MDButtonText(text=text, font_style="Body", role="large"),
            *args,
            **kwargs,
        )
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.height = "50dp"
        self.style = "elevated"


class PlaylistCreatorSnackbar(MDSnackbar):
    def __init__(self, *args, **kwargs):
        text = kwargs["text"]
        del kwargs["text"]
        sup_text = kwargs["sup_text"]
        del kwargs["sup_text"]
        action_text = kwargs.get("action_text")
        if action_text:
            del kwargs["action_text"]
        on_release = kwargs.get("on_release")
        if on_release:
            del kwargs["on_release"]
        if action_text and on_release:
            super().__init__(
                MDSnackbarText(text=text),
                MDSnackbarSupportingText(text=sup_text),
                MDSnackbarButtonContainer(
                    MDSnackbarActionButton(
                        MDSnackbarActionButtonText(text=action_text),
                        on_release=lambda x: on_release(),
                    ),
                    pos_hint={"center_y": 0.5},
                ),
                orientation="horizontal",
                *args,
                **kwargs,
            )
        else:
            super().__init__(
                MDSnackbarText(text=text),
                MDSnackbarSupportingText(text=sup_text),
                *args,
                **kwargs,
            )
        self.duration = 7
        self.style = "elevated"
        self.pos_hint = {"center_x": 0.5, "center_y": 0.15}
        self.size_hint_x = 0.7


class PlaylistCreatorInput(MDTextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.multiline = False
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        if not kwargs.get("size_hint_x"):
            self.size_hint_x = 0.6
        self.size_hint_min_x = 50

    def on_touch_down(self, touch):
        Window.softinput_mode = "pan"
        super().on_touch_down(touch)


class CheckItem(MDBoxLayout):
    text = StringProperty()
    group = StringProperty()
    id = StringProperty()
    active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.pos_hint = {"center_y": 0.5, "right_x": 1}
        self.spacing = "12dp"
        self.padding = "12dp"

        self.checkbox = MDCheckbox(
            group=self.group, active=self.active, pos_hint=self.pos_hint, id=self.id
        )
        self.checkbox.bind(active=self.set_active)
        self.label = PlaylistCreatorLabel(text=self.text, pos_hint=self.pos_hint)

        self.add_widget(self.checkbox)
        self.add_widget(self.label)

    def set_active(self, checkbox, value):
        self.active = value


class PlaylistCreatorTopBar(MDTopAppBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "small"
        self.size_hint_x = 1.0
        self.pos_hint = {"center_x": 0.5, "top": 1}
        app = MDApp.get_running_app()
        self.md_bg_color = app.theme_cls.onSecondaryContainerColor
        self.remove_widget(self.ids.title_box)

        user_icon_url = app.playlist_creator.sp.me()["images"][0]["url"]
        download_from_url(user_icon_url, os.path.join(app.storage_path, "user-icon.png"))
        leading_button = MDTopAppBarLeadingButtonContainer(
            FitImage(
                source=os.path.join(app.storage_path, "user-icon.png"),
                size_hint=(None, None),
                pos_hint={"left_x": 0.0, "center_y": 0.5},
                radius=["36dp", "36dp", "36dp", "36dp"],
                fit_mode="contain",
                size=("64dp", "64dp"),
            ),
            size_hint_x=0.5,
        )
        self.add_widget(leading_button)

        title = MDTopAppBarTitle(
            text="Playlist Creator",
            pos_hint={"center_x": 0.5},
            halign="center",
        )
        self.add_widget(title)

        trailing_buttons = MDTopAppBarTrailingButtonContainer(
            Widget(size_hint=(0.8, None)),
            MDActionTopAppBarButton(
                id="light",
                icon="weather-sunny",
                on_release=lambda x: app.set_theme("Light"),
                pos_hint={"center_y": 0.5},
                size_hint=(None, None),
            ),
            MDActionTopAppBarButton(
                id="dark",
                icon="moon-waxing-crescent",
                on_release=lambda x: app.set_theme("Dark"),
                size_hint=(None, None),
                pos_hint={"center_y": 0.5},
            ),
            size_hint_x=0.5,
            pos_hint={"right_x": 1},
            spacing="5dp",
        )
        self.add_widget(trailing_buttons)


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = self.theme_cls.secondaryContainerColor
        self.app = MDApp.get_running_app()
        self.app_top_bar = PlaylistCreatorTopBar()
        self.add_widget(self.app_top_bar)

        self.grid_layout = MDGridLayout(
            cols=1,
            spacing="16dp",
            padding="16dp",
            size_hint=(1, 0.9),
            pos_hint={"center_x": 0.5, "top": 0.9},
        )
        self.add_widget(self.grid_layout)

        self.command_layout = MDBoxLayout(size_hint=(1, 1), pos_hint={"x": 0.1, "y": 0.1})
        self.grid_layout.add_widget(self.command_layout)

        self.time_range_layout = MDBoxLayout(size_hint=(1, 1), pos_hint={"x": 0.1, "y": 0.1})
        self.grid_layout.add_widget(self.time_range_layout)

        self.limit_layout = MDBoxLayout(size_hint=(1, 1), pos_hint={"x": 0.1, "y": 0.1})
        self.grid_layout.add_widget(self.limit_layout)

        self.playlist_layout = MDBoxLayout(size_hint=(1, 1), pos_hint={"x": 0.1, "y": 0.1})
        self.grid_layout.add_widget(self.playlist_layout)

        self.friend_layout = MDBoxLayout(size_hint=(1, 1), pos_hint={"x": 0.1, "y": 0.1})
        self.grid_layout.add_widget(self.friend_layout)

        self.friend_playlist_layout = MDBoxLayout(size_hint=(1, 1), pos_hint={"x": 0.1, "y": 0.1})
        self.grid_layout.add_widget(self.friend_playlist_layout)

        # placeholders
        self.generate_button = None
        self.friend_playlist_button = None

        self.command_layout.add_widget(PlaylistCreatorLabel(text="Command"))

        self.command_button = PlaylistCreatorTextButton(text="Select command to execute...")
        menu_items = [
            {
                "text": "Get Top",
                "on_release": lambda x="Get Top": self.command_menu_callback(x),
            },
            {
                "text": "Get Recommendations",
                "on_release": lambda x="Get Recommendations": self.command_menu_callback(x),
            },
            {
                "text": "Blend With Friend",
                "on_release": lambda x="Blend With Friend": self.command_menu_callback(x),
            },
        ]
        self.command_menu = MDDropdownMenu(
            caller=self.command_button, items=menu_items, hor_growth="left"
        )
        self.command_button.bind(on_release=lambda x: self.command_menu.open())
        self.command_layout.add_widget(self.command_button)

        self.playlist_creator = self.app.playlist_creator
        self.username = self.playlist_creator.sp.me()["id"]

    def command_menu_callback(self, text):
        self.command_button.children[0].text = text
        self.command_menu.dismiss()
        self.show_additional_widgets(text)
        self.validate_parameters()

    def show_additional_widgets(self, text):
        self.time_range_layout.clear_widgets()
        self.limit_layout.clear_widgets()
        self.playlist_layout.clear_widgets()
        self.friend_layout.clear_widgets()
        self.friend_playlist_layout.clear_widgets()
        if self.generate_button:
            self.grid_layout.remove_widget(self.generate_button)
        self.time_range_layout.add_widget(PlaylistCreatorLabel(text="Time range"))
        self.time_range_button = PlaylistCreatorTextButton(text="Choose an interval...")
        time_range_items = [
            {
                "text": "Short term (~4 weeks)",
                "on_release": lambda x="Short term (~4 weeks)": self.time_range_callback(x),
            },
            {
                "text": "Medium term (~6 months)",
                "on_release": lambda x="Medium term (~6 months)": self.time_range_callback(x),
            },
            {
                "text": "Long term (~1 year)",
                "on_release": lambda x="Long term (~1 year)": self.time_range_callback(x),
            },
        ]
        self.time_range_menu = MDDropdownMenu(
            caller=self.time_range_button, items=time_range_items, hor_growth="left"
        )
        self.time_range_button.bind(on_release=lambda x: self.time_range_menu.open())
        self.time_range_layout.add_widget(self.time_range_button)

        self.limit_layout.add_widget(PlaylistCreatorLabel(text="Amount of tracks"))
        self.limit = PlaylistCreatorInput(
            hint_text="How many tracks a playlist should contain",
            text="50",
            input_filter="int",
            size_hint_x=0.2,
        )
        self.limit_layout.add_widget(self.limit)

        if text == "Get Recommendations":
            self.playlist_layout.clear_widgets()
            self.playlist_layout.add_widget(PlaylistCreatorLabel(text="Based on top..."))
            check_items_layout = MDBoxLayout(
                orientation="vertical",
                padding="12dp",
                spacing="12dp",
                pos_hint={"right_x": 1, "center_y": 0.5},
                size_hint=(0.3, 1),
                size_hint_min_x="200dp",
            )
            self.seed_type_tracks = CheckItem(
                text="tracks", active=True, id="top_tracks", group="seed_type"
            )
            check_items_layout.add_widget(self.seed_type_tracks)
            self.seed_type_artists = CheckItem(text="artists", id="top_artists", group="seed_type")
            check_items_layout.add_widget(self.seed_type_artists)
            self.playlist_layout.add_widget(check_items_layout)

        if text == "Blend With Friend":
            self.playlist_layout.clear_widgets()
            self.playlist_layout.add_widget(PlaylistCreatorLabel(text="Playlist"))
            playlists = self.get_playlists(self.app.username)
            self.playlist_button = PlaylistCreatorTextButton(text="Select playlist...")
            menu_items = [
                {
                    "text": item,
                    "on_release": lambda x=item: self.playlist_callback(x),
                }
                for item in playlists
            ]
            self.playlist_menu = MDDropdownMenu(
                caller=self.playlist_button, items=menu_items, hor_growth="left"
            )
            self.playlist_button.bind(on_release=lambda x: self.playlist_menu.open())
            self.playlist_layout.add_widget(self.playlist_button)

            self.friend_layout.add_widget(PlaylistCreatorLabel(text="Friend's username"))
            self.friend_input = PlaylistCreatorInput(
                hint_text="Spotify username of the user playlist of which should be blended with"
            )
            self.friend_ok_button = MDIconButton(
                icon="check-outline",
                style="tonal",
                md_bg_color="green",
                icon_color="white",
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            )
            self.friend_ok_button.bind(on_press=self.show_friend_playlists)
            self.friend_layout.add_widget(self.friend_input)
            self.friend_layout.add_widget(self.friend_ok_button)

        self.generate_button = MDButton(
            MDButtonText(
                text="Generate playlist",
                id="generate_text",
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                font_style="Title",
            ),
            MDButtonIcon(
                id="generate_icon",
                icon="cog",
                size=(0.5, 0.5),
                size_hint=(None, None),
                font_size="26sp",
            ),
            style="elevated",
            height="56dp",
            theme_width="Custom",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            disabled=True,
        )
        generate_icon = self.generate_button.get_ids()["generate_icon"]
        generate_icon.x = self.generate_button.get_ids()["generate_text"].width - (
            generate_icon.width + 10
        )
        self.generate_button.bind(on_release=self.generate_playlist)
        self.grid_layout.add_widget(self.generate_button)

    def validate_parameters(self):
        command = self.command_button.children[0].text
        match command:
            case "Get Top" | "Get Recommendations":
                if self.time_range_button.children[0].text in [
                    "Short term (~4 weeks)",
                    "Medium term (~6 months)",
                    "Long term (~1 year)",
                ]:
                    self.generate_button.disabled = False
                    for ch in self.generate_button.children:
                        ch.disabled = False
            case "Blend With Friend":
                if (
                    self.time_range_button.children[0].text
                    in [
                        "Short term (~4 weeks)",
                        "Medium term (~6 months)",
                        "Long term (~1 year)",
                    ]
                    and self.playlist_button.children[0].text != "Select playlist..."
                    and self.friend_input.text
                    and self.friend_playlist_button
                ):
                    self.generate_button.disabled = False
                    for ch in self.generate_button.children:
                        ch.disabled = False

    def get_playlists(self, username: str):
        playlists = self.playlist_creator.get_user_playlists(username)
        return [p["name"] for p in playlists["items"]]

    def generate_playlist(self, instance):
        time_range = self.time_range_button.children[0].text
        time_range_normalized = time_range.split(" (")[0].lower().replace(" ", "_")
        playlist, playlist_name = None, None
        match self.command_button.children[0].text:
            case "Get Top":
                top_tracks_ids = self.playlist_creator.get_top_tracks(
                    time_range_normalized, int(self.limit.text)
                )
                playlist_name = f"top_{time_range_normalized}_{str(date.today())}"
                playlist = self.playlist_creator.get_todays_top_playlist(
                    self.username, playlist_name
                )
                if not playlist:
                    if len(top_tracks_ids) == 0:
                        PlaylistCreatorSnackbar(
                            text="Can't generate playlist!",
                            sup_text="Not enough data exists for provided criteria.\nTry to change time range or listen more.",
                            background_color=self.theme_cls.onErrorContainerColor,
                        ).open()
                        raise UserInputError(f"No top tracks found for {time_range_normalized}")
                    playlist = self.playlist_creator.create_playlist(
                        playlist_name,
                        f"Generated by PlaylistCreator for {time_range}",
                        top_tracks_ids,
                    )

            case "Get Recommendations":
                description = "Generated by PlaylistCreator based on "
                if self.seed_type_tracks.active:
                    top_tracks_ids = self.playlist_creator.get_top_tracks(
                        time_range_normalized, int(self.limit.text)
                    )
                    if len(top_tracks_ids) < 5:
                        PlaylistCreatorSnackbar(
                            text="Can't generate playlist!",
                            sup_text="Not enough data exists for provided criteria.\nTry to change time range or listen more.",
                            background_color=self.theme_cls.onErrorContainerColor,
                        ).open()
                        raise UserInputError(
                            f"Not enough top tracks found for {time_range_normalized}"
                        )
                    seed_tracks_ids = random.choices(top_tracks_ids, k=5)
                    result = self.playlist_creator.get_recommendations(
                        seed_tracks=seed_tracks_ids, limit=int(self.limit.text), country="SE"
                    )
                    seed_tracks = [self.playlist_creator.sp.track(i) for i in seed_tracks_ids]
                    artist_tracks = [
                        f"{t['artists'][0]['name']} - {t['name']}" for t in seed_tracks
                    ]
                    description += f"tracks from my {time_range} top: {', '.join(artist_tracks)}"
                else:
                    top_artists_ids = self.playlist_creator.get_top_artists(
                        time_range_normalized, 5
                    )
                    result = self.playlist_creator.get_recommendations(
                        seed_artists=top_artists_ids, limit=int(self.limit.text), country="SE"
                    )
                    seed_artists = [self.playlist_creator.sp.artist(i) for i in top_artists_ids]
                    description += f"my {time_range} top artists: {', '.join([a['name'] for a in seed_artists])}"
                tracks_ids = [t["id"] for t in result["tracks"]]
                playlist_name = f"recommendations_{str(date.today())}"
                playlist = self.playlist_creator.create_playlist(
                    playlist_name,
                    description,
                    tracks_ids,
                )

            case "Blend With Friend":
                playlist = self.playlist_creator.make_blend(
                    self.friend_input.text,
                    self.friend_playlist_button.children[0].text,
                    self.playlist_button.children[0].text,
                    int(self.limit.text),
                )
                playlist_name = playlist["name"]

        if playlist:
            if self.app.platform == "android":
                PlaylistCreatorSnackbar(
                    text="Playlist is generated",
                    sup_text=f"Try out now: {playlist_name}!",
                    background_color=self.theme_cls.onPrimaryContainerColor,
                    action_text="Play",
                    on_release=self.app.play_playlist(playlist["id"]),
                ).open()
            else:
                PlaylistCreatorSnackbar(
                    text="Playlist is generated",
                    sup_text=f"Try out now: {playlist_name}!",
                    background_color=self.theme_cls.onPrimaryContainerColor,
                ).open()
        else:
            PlaylistCreatorSnackbar(
                text="Something went wrong :(",
                sup_text="Error report is sent to developer",
                background_color=self.theme_cls.onErrorContainerColor,
            ).open()
            raise PlaylistCreatorError(
                "Couldn't create playlist",
                username=self.username,
                command=self.command_button.children[0].text,
                time_range=time_range,
                playlist_name=playlist_name,
            )

    def time_range_callback(self, text):
        self.time_range_button.children[0].text = text
        self.time_range_menu.dismiss()
        self.validate_parameters()

    def playlist_callback(self, text):
        self.playlist_button.children[0].text = text
        self.playlist_menu.dismiss()
        self.validate_parameters()

    def show_friend_playlists(self, instance):
        if instance.text.strip():
            friend = self.friend_input.text
            try:
                self.playlist_creator.sp.user(friend)
            except Exception:
                Logger.error(f"User {friend} seems to not exist")
                PlaylistCreatorSnackbar(
                    text="User seems to not exist",
                    sup_text=f"User with id {friend} is not found. Check your input and try again.",
                    background_color=self.theme_cls.onErrorContainerColor,
                ).open()
                self.friend_input.error = True
                self.friend_playlist_layout.clear_widgets()
            else:
                self.friend_playlist_layout.add_widget(
                    PlaylistCreatorLabel(text="Friend's playlist name")
                )
                playlists = self.get_playlists(self.friend_input.text)
                self.friend_playlist_button = PlaylistCreatorTextButton(text="Select playlist...")
                menu_items = [
                    {
                        "text": item,
                        "on_release": lambda x=item: self.friend_playlist_callback(x),
                    }
                    for item in playlists
                ]
                self.friend_playlist_menu = MDDropdownMenu(
                    caller=self.friend_playlist_button, items=menu_items, hor_growth="left"
                )
                self.friend_playlist_button.bind(
                    on_release=lambda x: self.friend_playlist_menu.open()
                )
                self.friend_playlist_layout.add_widget(self.friend_playlist_button)

    def friend_playlist_callback(self, text):
        self.friend_playlist_button.children[0].text = text
        self.friend_playlist_menu.dismiss()
        self.validate_parameters()
