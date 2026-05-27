[app]

title = LotoDaSorte
package.name = lotodasorte
package.domain = org.lotodasorte
source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,kv,atlas,json
version = 1.0
entrypoint = main.py
requirements = python3,kivy==2.3.0
android.presplash_color = #0D0020
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
