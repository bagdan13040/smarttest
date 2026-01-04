[app]
# (str) Title of your application
title = Kivy App

# (str) Package name
package.name = kivyapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py is located
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using pattern matching
source.include_patterns = .env

# (str) Application versioning (method 1)
version = 1.4

# (list) Application requirements
# requests + certifi needed for proper SSL/DNS resolution on Android
# plyer for native features (file picker, camera, etc.)
requirements = python3,kivy==2.2.1,kivymd==1.2.0,python-dotenv,certifi,pyjnius,plyer,requests

# (str) Icon of the application
icon.filename = assets/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (str) Supported Android API
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version
android.ndk = 25b

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android entry point, default is ok
android.entrypoint = org.kivy.android.PythonActivity

# (str) Presplash image
# presplash.filename = assets/presplash.png

# (str) The package Python version
# (not needed when building with buildozer on newer toolchains)
p4a.branch = master
p4a.python_version = 3.10

# Android permissions (MUST be in [app] section!)
# READ_MEDIA_IMAGES - for Android 13+ (API 33+) to access images
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, READ_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

[buildozer]
log_level = 2
warn_on_root = 1
