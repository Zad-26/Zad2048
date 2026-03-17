"""
Zad 2048 - Board Manager Module
Handles persistence of game state, settings, and statistics
using local JSON storage.
"""

import json
import os


STORAGE_DIR   = os.path.join(os.path.dirname(__file__), "storage")
SETTINGS_FILE = os.path.join(STORAGE_DIR, "settings.json")
STATS_FILE    = os.path.join(STORAGE_DIR, "stats.json")


class StorageManager:
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        self._ensure_files()

    def _ensure_files(self):
        if not os.path.exists(SETTINGS_FILE):
            self._write_json(SETTINGS_FILE, self._default_settings())
        if not os.path.exists(STATS_FILE):
            self._write_json(STATS_FILE, self._default_stats())

    def _default_settings(self):
        return {"theme": "dark", "sound_enabled": True, "animations_enabled": True, "bgm_enabled": True, "sfx_volume": 0.70, "bgm_volume": 0.30}

    def _default_stats(self):
        return {"best_score": 0, "highest_tile": 0, "total_games": 0, "total_moves": 0}

    def _read_json(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def get_settings(self):
        data = self._read_json(SETTINGS_FILE)
        d = self._default_settings()
        d.update(data)
        return d

    def save_settings(self, s):
        self._write_json(SETTINGS_FILE, s)

    def get_setting(self, key, default=None):
        return self.get_settings().get(key, default)

    def set_setting(self, key, value):
        s = self.get_settings()
        s[key] = value
        self.save_settings(s)

    def get_stats(self):
        data = self._read_json(STATS_FILE)
        d = self._default_stats()
        d.update(data)
        return d

    def save_stats(self, stats):
        self._write_json(STATS_FILE, stats)

    def get_best_score(self):
        return self.get_stats().get("best_score", 0)

    def reset_stats(self):
        self.save_stats(self._default_stats())


class ColorManager:
    """
    Tile color palette + dynamic color generation for values beyond 2048.
    Text colors are always chosen for maximum contrast/readability.
    """

    # ── Dark theme: deep, neon-tinted ─────────────────────────────────────
    DARK_TILE_COLORS = {
        0:    (0.20, 0.15, 0.34, 1),   # Empty — dark violet
        2:    (0.28, 0.22, 0.48, 1),   # Soft indigo
        4:    (0.38, 0.18, 0.62, 1),   # Medium violet
        8:    (0.85, 0.42, 0.08, 1),   # Neon orange
        16:   (0.90, 0.30, 0.08, 1),   # Hot orange-red
        32:   (0.88, 0.14, 0.18, 1),   # Neon red
        64:   (0.70, 0.08, 0.12, 1),   # Deep crimson
        128:  (0.88, 0.72, 0.05, 1),   # Neon gold
        256:  (0.95, 0.82, 0.08, 1),   # Bright yellow
        512:  (0.08, 0.78, 0.45, 1),   # Neon green
        1024: (0.08, 0.48, 0.92, 1),   # Neon blue
        2048: (0.72, 0.08, 0.92, 1),   # Neon purple
    }

    # ── Light theme: vivid, saturated — enough contrast on white bg ───────
    LIGHT_TILE_COLORS = {
        0:    (0.82, 0.78, 0.88, 1),   # Empty — soft lilac
        2:    (0.90, 0.86, 0.96, 1),   # Pale lavender
        4:    (0.98, 0.88, 0.72, 1),   # Warm peach
        8:    (0.97, 0.65, 0.35, 1),   # Vivid orange
        16:   (0.96, 0.50, 0.22, 1),   # Deep orange
        32:   (0.94, 0.30, 0.22, 1),   # Bold red-orange
        64:   (0.85, 0.14, 0.10, 1),   # Rich red
        128:  (0.95, 0.78, 0.20, 1),   # Golden yellow
        256:  (0.92, 0.70, 0.05, 1),   # Deep gold
        512:  (0.15, 0.72, 0.38, 1),   # Forest green
        1024: (0.15, 0.42, 0.88, 1),   # Royal blue
        2048: (0.55, 0.10, 0.85, 1),   # Bold purple
    }

    # ── Text colors — simple rule: dark tiles get white, light get dark ───
    # We compute these dynamically based on luminance instead of a lookup.

    @classmethod
    def _luminance(cls, r, g, b):
        """Perceived luminance (0=black, 1=white)."""
        return 0.299 * r + 0.587 * g + 0.114 * b

    @classmethod
    def get_text_color(cls, value, theme="dark"):
        """
        Always return maximum-contrast text color for a given tile.
        White text on dark tiles, dark text on light tiles.
        """
        tile_color = cls.get_tile_color(value, theme)
        r, g, b = tile_color[0], tile_color[1], tile_color[2]
        lum = cls._luminance(r, g, b)
        if value == 0:
            # Empty tile — very subtle text (no number anyway)
            return (0.55, 0.50, 0.65, 0.0)   # fully transparent for empty
        if lum > 0.55:
            # Light tile background → dark text
            return (0.18, 0.10, 0.32, 1)
        else:
            # Dark tile background → white text
            return (1.0, 1.0, 1.0, 1)

    @classmethod
    def _generate_dynamic_color(cls, value, theme="dark"):
        """Generate a unique color for tile values beyond 2048."""
        import math
        steps = int(math.log2(value)) - 11
        hue = (steps * 0.17) % 1.0
        sat = 0.80 if theme == "dark" else 0.70
        val = 0.92 if theme == "dark" else 0.82

        h = hue * 6
        i = int(h)
        f = h - i
        p = val * (1 - sat)
        q = val * (1 - sat * f)
        t = val * (1 - sat * (1 - f))

        sectors = [(val,t,p),(q,val,p),(p,val,t),(p,q,val),(t,p,val),(val,p,q)]
        r, g, b = sectors[i % 6]
        return (r, g, b, 1)

    @classmethod
    def get_tile_color(cls, value, theme="dark"):
        colors = cls.DARK_TILE_COLORS if theme == "dark" else cls.LIGHT_TILE_COLORS
        if value in colors:
            return colors[value]
        return cls._generate_dynamic_color(value, theme)

    @classmethod
    def get_tile_font_size(cls, value):
        if value < 100:   return 36
        if value < 1000:  return 30
        if value < 10000: return 24
        return 18