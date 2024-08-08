[app]

title = Playlist Creator
package.name = playlistcreator
package.domain = org.misanthropicat
source.dir = src
source.include_exts = py,svg,png,json,env
source.include_patterns = data/*
source.exclude_patterns = migrator.py
version.regex = ([0-9]+.[0-9]+.[0-9]+)
version.filename = %(source.dir)s/VERSION
requirements = python3==3.11.9, kivy==2.3.0, spotipy==2.24.0, redis==5.0.7, https://github.com/kivymd/KivyMD/archive/master.zip, materialyoucolor==2.0.9, asynckivy==0.6.3, asyncgui==0.6.3, python-dotenv==1.0.1, pyjnius==1.6.1, requests==2.32.3
presplash.filename = %(source.dir)s/data/splash_win.gif
icon.filename = %(source.dir)s/data/app_icon.png
orientation = portrait

osx.python_version = 3
osx.kivy_version = 1.9.1

fullscreen = 0
android.presplash_color = darkgray
android.presplash_lottie = src/data/presplash.json

icon.adaptive_background.filename = %(source.dir)s/src/data/icon_bg.png
android.permissions = android.permission.INTERNET, android.permission.READ_EXTERNAL_STORAGE, android.permission.WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 28
android.ndk = 25b
android.ndk_api = 28
android.private_storage = True
android.ndk_path = 
android.sdk_path = 
android.ant_path =
android.skip_update = False
android.accept_sdk_license = True
android.add_resources = src/data/icon.svg
android.enable_androidx = True
android.logcat_filters = *:S python:D
android.logcat_pid_only = True
android.archs = arm64-v8a,armeabi-v7a,x86,x86_64
android.allow_backup = True

p4a.branch = develop
p4a.bootstrap = sdl2

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false


[buildozer]
log_level = 2
warn_on_root = 1
