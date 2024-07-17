import logging
import os
import random
import sys

import kivy

kivy.require("2.3.0")

from kivy.base import ExceptionHandler, ExceptionManager
from kivy.config import Config
from kivy.utils import platform
from kivymd.app import MDApp

if platform == "android":
    sys.path.append(os.getcwd())
    from components import MainScreen
    from playlist_creator import PlaylistCreator
    from utils import handle_exception
else:
    from src import MainScreen, PlaylistCreator, handle_exception

os.environ["KIVY_LOG_MODE"] = "MIXED"
logging.basicConfig(level=logging.DEBUG)


class PlaylistCreatorApp(MDApp):
    all_colors = [
        "Aqua",
        "Aquamarine",
        "Blue",
        "Blueviolet",
        "Cadetblue",
        "Cornflowerblue",
        "Cyan",
        "Darkblue",
        "Darkcyan",
        "Darkseagreen",
        "Darkslateblue",
        "Darkturquoise",
        "Darkviolet",
        "Deepskyblue",
        "Dodgerblue",
        "Lightblue",
        "Lightcyan",
        "Lightseagreen",
        "Lightskyblue",
        "Lightsteelblue",
        "Mediumaquamarine",
        "Mediumblue",
        "Mediumpurple",
        "Mediumseagreen",
        "Mediumslateblue",
        "Mediumturquoise",
        "Midnightblue",
        "Navy",
        "Paleturquoise",
        "Powderblue",
        "Royalblue",
        "Seagreen",
        "Skyblue",
        "Slateblue",
        "Steelblue",
        "Teal",
        "Turquoise",
    ]

    @handle_exception
    def build(self):
        self.theme_cls.primary_hue = "A200"
        self.set_theme("Dark")
        self.theme_cls.theme_style_switch_animation = True
        if platform == "android":
            from android import mActivity
            from android.storage import app_storage_path

            context = mActivity.getApplicationContext()
            result = context.getExternalFilesDir(None)
            storage_path = str(result.toString()) if result else app_storage_path()

            os.environ["SPOTIPY_CLIENT_ID"] = "b2ec6891adb04433bc49d681cda930ed"
            os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8888/callback"
        else:
            from dotenv import load_dotenv

            load_dotenv()

        self.storage_path = storage_path if platform == "android" else os.getcwd()
        os.environ["STORAGE_PATH"] = self.storage_path
        logging.debug(
            f"Storage path: {self.storage_path}\nStorage path content: {os.listdir(self.storage_path)}"
        )
        self.icon = os.path.join(self.storage_path, "data", "icon.svg")
        Config.set("kivy", "log_dir", os.path.join(self.storage_path, "logs"))
        Config.set("kivy", "log_name", "kivy_%y-%m-%d_%_.txt")
        Config.set("kivy", "log_maxfiles", 100)
        Config.set("kivy", "log_level", "debug")
        Config.set("kivy", "log_enable", 1)
        self.playlist_creator = PlaylistCreator(platform)
        self.username = self.playlist_creator.sp.me()["id"]
        return MainScreen()

    def on_start(self):
        def on_start(*args):
            self.root.md_bg_color = self.theme_cls.backgroundColor

    def on_pause(self):
        return True

    def set_theme(self, theme):
        self.theme_cls.theme_style = theme
        self.theme_cls.primary_palette = random.choice(self.all_colors)
        self.theme_cls.accent_palette = random.choice(self.all_colors)
        if self.root:
            self.root.md_bg_color = self.theme_cls.primaryContainerColor


class E(ExceptionHandler):
    def handle_exception(self, inst):
        logging.exception("Exception caught by ExceptionHandler")
        return ExceptionManager.PASS


ExceptionManager.add_handler(E())

if __name__ == "__main__":
    PlaylistCreatorApp().run()
