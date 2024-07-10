import os
import random
import kivy

kivy.require("2.3.0")

from datetime import date
from dotenv import load_dotenv
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton, MDButtonIcon
from kivymd.uix.slider.slider import MDSlider, MDSliderValueLabel, MDSliderHandle
from kivymd.uix.snackbar.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.appbar.appbar import (
    MDTopAppBar,
    MDTopAppBarTitle,
    MDTopAppBarLeadingButtonContainer,
)
from kivymd.uix.segmentedbutton import MDSegmentedButton, MDSegmentButtonIcon, MDSegmentedButtonItem

from .playlist_creator import PlaylistCreator


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
        super().__init__(
            MDSnackbarText(text=text),
            *args,
            **kwargs,
        )
        self.duration = 7
        self.style = "elevated"
        self.pos_hint = {"center_x": 0.5, "center_y": 0.1}
        self.size_hint_x = 0.7


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        """ self.switch_theme_button = MDSegmentedButton(
            MDSegmentedButtonItem(
                MDSegmentButtonIcon(icon="moon-waning-crescent"),
                id="theme-dark",
            ),
            MDSegmentedButtonItem(
                MDSegmentButtonIcon(icon="language-python"),
                id="theme-light",
                on_active=self.switch_theme_button,
            ),
            id="switch-theme",
            type="large",
            size_hint_x=0.2,
            pos_hint={"center_x": 0.8, "center_y": 0.5},
        ) """
        self.app_top_bar = MDTopAppBar(
            MDTopAppBarTitle(text="PlaylistCreator", pos_hint={"center_x": 0.5}, halign="center"),
            type="small",
            size_hint_x=1.0,
            pos_hint={"center_x": 0.5, "center_y": 0.95},
            spacing="16dp",
            padding="16dp",
        )
        self.add_widget(self.app_top_bar)

        self.grid_layout = MDGridLayout(
            cols=1,
            spacing="16dp",
            padding="16dp",
            size_hint=(1, 1),
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

        self.generate_button = None  # placeholder

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

        self.playlist_creator = PlaylistCreator()
        self.username = self.playlist_creator.sp.me()["id"]

    def command_menu_callback(self, text):
        self.command_button.children[0].text = text
        self.command_menu.dismiss()
        self.show_additional_widgets(text)

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
                "text": "Short term",
                "on_release": lambda x="Short term": self.time_range_callback(x),
            },
            {
                "text": "Medium term",
                "on_release": lambda x="Medium term": self.time_range_callback(x),
            },
            {
                "text": "Long term",
                "on_release": lambda x="Long term": self.time_range_callback(x),
            },
        ]
        self.time_range_menu = MDDropdownMenu(
            caller=self.time_range_button, items=time_range_items, hor_growth="left"
        )
        self.time_range_button.bind(on_release=lambda x: self.time_range_menu.open())
        self.time_range_layout.add_widget(self.time_range_button)

        self.limit_layout.add_widget(PlaylistCreatorLabel(text="Amount of tracks"))
        self.limit = MDSlider(
            MDSliderValueLabel(),
            MDSliderHandle(),
            min=1,
            max=1000,
            step=1,
            value=50,
            size_hint_x=0.75,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.limit_layout.add_widget(self.limit)

        if text == "Blend With Friend":
            self.playlist_layout.clear_widgets()
            self.playlist_layout.add_widget(PlaylistCreatorLabel(text="Playlist"))
            playlists = self.get_playlists(self.username)
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
            self.friend_input = MDTextField(
                multiline=False,
                hint_text="Spotify username of the user playlist of which should be blended with",
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                size_hint_x=0.6,
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
            style="tonal",
            height="56dp",
            theme_width="Custom",
            size_hint_x=0.5,
        )
        generate_icon = self.generate_button.get_ids()["generate_icon"]
        generate_icon.x = self.generate_button.get_ids()["generate_text"].get_center_x() - (
            generate_icon.width + 0.1
        )
        self.generate_button.bind(on_press=self.generate_playlist)
        self.grid_layout.add_widget(self.generate_button)

    def get_playlists(self, username: str):
        playlists = self.playlist_creator.get_user_playlists(username)
        return [p["name"] for p in playlists["items"]]

    def generate_playlist(self, instance):
        time_range = self.time_range_button.children[0].text
        time_range_normalized = time_range.lower().replace(" ", "_")
        match self.command_button.children[0].text:
            case "Get Top":
                top_tracks_ids = self.playlist_creator.get_top_tracks(
                    time_range_normalized, self.limit.value
                )
                playlist_name = f"top_{time_range_normalized}_{str(date.today())}"
                playlist = self.playlist_creator.get_todays_top_playlist(
                    self.username, playlist_name
                )
                if not playlist:
                    playlist = self.playlist_creator.create_playlist(
                        playlist_name,
                        f"Generated by PlaylistCreator for {time_range}",
                        top_tracks_ids,
                    )

            case "Get Recommendations":
                top_tracks_ids = self.playlist_creator.get_top_tracks(
                    time_range_normalized, self.limit.value
                )
                seed_tracks = random.choices(top_tracks_ids, k=5)
                result = self.playlist_creator.get_recommendations(
                    seed_tracks=seed_tracks, limit=self.limit.value, country="SE"
                )
                tracks_ids = [t["id"] for t in result["tracks"]]
                playlist_name = f"recommendations_{str(date.today())}"
                playlist = self.playlist_creator.create_playlist(
                    playlist_name,
                    f"Generated by PlaylistCreator based on 5 random tracks from my current {time_range} top",
                    tracks_ids,
                )

            case "Blend With Friend":
                playlist_name = self.playlist_creator.make_blend(
                    self.friend_input.text,
                    self.friend_playlist_button.children[0].text,
                    self.playlist_button.children[0].text,
                    self.limit.value,
                )
                playlist = self.playlist_creator.get_playlist_by_name(self.username, playlist_name)

        if playlist:
            PlaylistCreatorSnackbar(
                text=f"Playlist {playlist_name} is successfully generated. Enjoy!",
                background_color=self.theme_cls.onPrimaryContainerColor,
            ).open()
        else:
            PlaylistCreatorSnackbar(
                text="Something went wrong. :( Please, let know the developer: helgamogish@gmail.com",
                background_color=self.theme_cls.onErrorColor,
            )

    def time_range_callback(self, text):
        self.time_range_button.children[0].text = text
        self.time_range_menu.dismiss()

    def playlist_callback(self, text):
        self.playlist_button.children[0].text = text
        self.playlist_menu.dismiss()

    def show_friend_playlists(self, instance):
        if instance.text.strip():
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
            self.friend_playlist_button.bind(on_release=lambda x: self.friend_playlist_menu.open())
            self.friend_playlist_layout.add_widget(self.friend_playlist_button)

    def friend_playlist_callback(self, text):
        self.friend_playlist_button.children[0].text = text
        self.friend_playlist_menu.dismiss()


class PlaylistCreatorApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.dynamic_color = True
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.primary_palette = "Teal"
        self.icon = os.path.join(os.getcwd(), "data", "icon.svg")
        return MainScreen()


if __name__ == "__main__":
    load_dotenv()
    PlaylistCreatorApp().run()
