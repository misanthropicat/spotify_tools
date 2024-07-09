import os
import kivy

kivy.require("2.3.0")

from dotenv import load_dotenv
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.slider.slider import MDSlider, MDSliderValueLabel, MDSliderHandle

from .playlist_creator import PlaylistCreator


class MyLabel(MDLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.adaptive_size = True
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.font_style = "Body"
        self.role = "large"
        self.valign = "center"


class MyTextButton(MDButton):
    def __init__(self, *args, **kwargs):
        text = kwargs["text"]
        del kwargs["text"]
        super().__init__(MDButtonText(text=text), *args, **kwargs)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.height = "50dp"
        self.style = "elevated"


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.grid_layout = MDGridLayout(
            cols=1,
            spacing="16dp",
            padding="16dp",
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
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

        self.command_layout.add_widget(MyLabel(text="Command"))

        self.command_button = MyTextButton(text="Select command to execute...")
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
        self.time_range_layout.add_widget(MyLabel(text="Time range"))
        self.time_range_button = MyTextButton(text="Choose an interval...")
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

        self.limit_layout.add_widget(MyLabel(text="Amount of tracks"))
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
            self.playlist_layout.add_widget(MyLabel(text="Playlist"))
            playlists = self.get_playlists(self.username)
            self.playlist_button = MyTextButton(text="Select playlist...")
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

            self.friend_layout.add_widget(MyLabel(text="Friend's username"))
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

    def get_playlists(self, username: str):
        playlists = self.playlist_creator.get_user_playlists(username)
        return [p["name"] for p in playlists["items"]]

    def time_range_callback(self, text):
        self.time_range_button.children[0].text = text
        self.time_range_menu.dismiss()

    def playlist_callback(self, text):
        self.playlist_button.children[0].text = text
        self.playlist_menu.dismiss()

    def show_friend_playlists(self, instance):
        if instance.text.strip():
            self.friend_playlist_layout.add_widget(MyLabel(text="Friend's playlist name"))
            playlists = self.get_playlists(self.friend_input.text)
            self.friend_playlist_button = MyTextButton(text="Select playlist...")
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
        self.theme_cls.primary_palette = "Teal"
        self.icon = os.path.join(os.getcwd(), "data", "icon.svg")
        return MainScreen()

    def theme_switch(self):
        self.theme_cls.switch_theme()


if __name__ == "__main__":
    load_dotenv()
    PlaylistCreatorApp().run()
