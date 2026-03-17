# Zad 2048 🎮

> A premium, modern mobile implementation of the classic 2048 puzzle game — built with Python & Kivy.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Kivy](https://img.shields.io/badge/Kivy-2.3.0-brightgreen?logo=kivy)
![License](https://img.shields.io/badge/License-MIT-purple)
![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20Desktop-orange)

---

## 📱 Screenshots

| Splash | Game | Settings | Game Over |
|--------|------|----------|-----------|
| *(splash screenshot)* | *(game screenshot)* | *(settings screenshot)* | *(game over screenshot)* |

---

## ✨ Features

### Core Gameplay
- Classic 2048 rules on a 4×4 grid
- Swipe gestures (or arrow keys on desktop)
- Tile merging with satisfying animations
- Undo last move
- New game / restart button

### Visual Design
- 🌙 **Dark Mode** — deep purple background, neon-like tile glow
- ☀️ **Light Mode** — soft pastel background, bright vibrant tiles
- Smooth animated gradient background (slowly shifts colors)
- Rounded tile corners with per-value color palette
- Dynamic color generation for tiles beyond 2048 (4096, 8192, etc.)

### Animations
- Tile slide (ease-out cubic)
- Merge pop (scale bounce)
- New tile spawn (out-back bounce)
- Button press feedback
- Game over / victory screen fade-in

### Particle Effects
- Glowing particle burst on every tile merge
- Particles match tile color and fade in ~0.5 seconds

### Persistence
- Best score saved locally
- Full statistics (games played, moves made, highest tile)
- Theme and sound preferences saved across sessions

### Settings Screen
- Toggle Dark / Light mode
- Enable / Disable sound effects
- Enable / Disable animations
- View and reset game statistics

---

## 🗂️ Project Structure

```
Zad2048/
├── main.py                  # App entry point & screen manager
├── game_logic.py            # Core 2048 game engine
├── board_manager.py         # Storage & color management
├── animation_manager.py     # All Kivy animations
├── particle_system.py       # Merge particle effects
│
├── ui/
│   ├── splash_screen.py     # Animated title screen
│   ├── game_screen.py       # Main game UI & board
│   ├── settings_screen.py   # Settings & statistics
│   └── game_over_screen.py  # Game over & victory overlays
│
├── assets/
│   ├── sounds/              # .wav sound effects
│   ├── fonts/               # Custom font files
│   └── images/              # Icons, presplash images
│
├── storage/
│   ├── settings.json        # User preferences
│   └── stats.json           # Game statistics
│
├── buildozer.spec           # Android build configuration
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Zad2048.git
cd Zad2048
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** On some systems you may need additional system packages for Kivy.
> See the [Kivy Installation Guide](https://kivy.org/doc/stable/gettingstarted/installation.html).

### 4. Run the Game

```bash
python main.py
```

Use arrow keys or swipe (on touch devices) to play.

---

## 📦 Build Android APK with Buildozer

### Prerequisites (Linux recommended)

```bash
# Install Buildozer
pip install buildozer

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    python3-pip build-essential git \
    libffi-dev libssl-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    zlib1g-dev openjdk-17-jdk autoconf libtool pkg-config
```

### Build Debug APK

```bash
cd Zad2048
buildozer android debug
```

The APK will appear in the `bin/` directory.

### Build Release APK

```bash
buildozer android release
```

> The first build downloads the Android SDK/NDK (~1–2 GB) and takes 10–30 minutes.
> Subsequent builds are much faster.

### Deploy to Connected Device

```bash
buildozer android debug deploy run
```

---

## 🎨 Tile Color Palette

| Tile  | Dark Mode             | Light Mode            |
|-------|-----------------------|-----------------------|
| 2     | Dark gray-blue        | Near white            |
| 4     | Muted purple          | Soft peach            |
| 8     | Neon orange           | Orange                |
| 16    | Hot orange            | Deep orange           |
| 32    | Neon red              | Coral red             |
| 64    | Deep neon red         | Red-orange            |
| 128   | Neon yellow           | Gold yellow           |
| 256   | Bright neon yellow    | Bright gold           |
| 512   | Neon green            | Deep gold             |
| 1024  | Neon blue             | Green                 |
| 2048  | Neon purple           | Purple                |
| 4096+ | Auto-generated (HSV)  | Auto-generated (HSV)  |

---

## 🔊 Sound Effects

Place your `.wav` audio files in `assets/sounds/`:

| File          | When played         |
|---------------|---------------------|
| `move.wav`    | Any tile slides     |
| `merge.wav`   | Two tiles merge     |
| `score.wav`   | Score increases     |
| `win.wav`     | Player reaches 2048 |
| `gameover.wav`| No moves remaining  |

Free sound packs compatible with this project:
- [Freesound.org](https://freesound.org)
- [OpenGameArt.org](https://opengameart.org)

---

## 🔧 Configuration

Edit `storage/settings.json` to set defaults before first launch:

```json
{
  "theme": "dark",
  "sound_enabled": true,
  "animations_enabled": true
}
```

---

## 🛣️ Roadmap / Future Improvements

- [ ] 5×5 and 6×6 board variants
- [ ] Swipe gesture speed detection for faster animations
- [ ] Cloud sync for scores
- [ ] Leaderboard screen
- [ ] Custom color themes / skins
- [ ] Haptic feedback on Android
- [ ] Achievements system
- [ ] Animated tile number font (custom TTF)
- [ ] iOS build support

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/awesome-feature`)
3. Commit your changes (`git commit -m 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/awesome-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Credits

- Original 2048 game by [Gabriele Cirulli](https://github.com/gabrielecirulli/2048)
- Built with [Kivy](https://kivy.org/) — Open source Python UI framework
- Color palette inspired by the original 2048 web game

---

*Made with ❤️ and Python*
