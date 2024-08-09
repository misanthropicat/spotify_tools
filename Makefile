clean-android:
	buildozer android clean

build-android: clean-android
	buildozer android debug

build-win:
	py -3.11 -m PyInstaller playlistcreator.spec
