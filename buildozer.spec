[app]

title = Zad 2048
package.name = zad2048
package.domain = org.zad2048
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,wav,mp3
version = 1.0.0

requirements = python3,kivy==2.3.0,pygame,pillow

source.include_patterns = assets/*,assets/sounds/*,assets/fonts/*,assets/images/*,storage/*,ui/*.py

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
android.arch = arm64-v8a
android.archs = arm64-v8a

icon.filename = %(source.dir)s/assets/images/icon.png
presplash.filename = %(source.dir)s/assets/images/icon.png
android.presplash_color = #120832

android.gradle_dependencies =
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = .buildozer
bin_dir = ./bin
