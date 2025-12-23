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
version = 0.8

# (list) Application requirements
requirements = python3,kivy,requests,python-dotenv,urllib3,charset_normalizer,idna,certifi

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

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
# (str) Add extra permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,ACCESS_NETWORK_STATE
