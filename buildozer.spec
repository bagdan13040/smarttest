[app]
# (str) Title of your application
title = Kivy App

# (str) Package name
package.name = kivyapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py is located
source.dir = .

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy,requests

# (str) Icon of the application
icon.filename = assets/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (str) Supported Android API
android.api = 31

# (str) Android NDK version
android.ndk = 23b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android entry point, default is ok
android.entrypoint = org.kivy.android.PythonActivity

# (str) Presplash image
# presplash.filename = assets/presplash.png

# (str) The package Python version
# (not needed when building with buildozer on newer toolchains)

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
# (str) Add extra permissions
android.permissions = INTERNET
