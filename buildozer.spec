[app]

# ── Basic App Info ─────────────────────────────────────────────────────────
title = Zad 2048
package.name = zad2048
package.domain = org.zad2048
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,wav,mp3

# App version
version = 1.0.0

# ── Dependencies ───────────────────────────────────────────────────────────
requirements = python3,kivy==2.3.0,kivymd

# ── Assets ────────────────────────────────────────────────────────────────
# Include all asset directories
source.include_patterns = assets/*,assets/sounds/*,assets/fonts/*,assets/images/*,assets/images/icon.png,assets/images/zad_photo.png,storage/*,ui/*.py

# ── Orientation & Display ─────────────────────────────────────────────────
orientation = portrait
fullscreen = 0

# ── Android Settings ──────────────────────────────────────────────────────
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
android.arch = arm64-v8a

# Gradle version
android.gradle_dependencies =

# ── Icon & Presplash ─────────────────────────────────────────────────────
# Uncomment and set your own icon paths:
icon.filename = %(source.dir)s/assets/images/icon.png
presplash.filename = %(source.dir)s/assets/images/icon.png

# Presplash background color (hex)
android.presplash_color = #1208323

# ── iOS Settings (optional) ───────────────────────────────────────────────
# ios.kivy_ios_url = https://github.com/kivy/kivy-ios
# ios.kivy_ios_branch = master

# ── Build Configuration ───────────────────────────────────────────────────
[buildozer]
log_level = 2
warn_on_root = 1

# Build directory
build_dir = .buildozer

# Bin directory (output APK location)
bin_dir = ./bin
