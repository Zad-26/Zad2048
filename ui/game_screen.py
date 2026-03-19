"""
Zad 2048 - Game Screen
- Score-driven background color (dark + light mode)
- Buttons centered
- Sound effects + looping background music via pygame
- Canvas-drawn tile text (no floating labels)
"""

import os, sys

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp

from game_logic import GameLogic
from board_manager import StorageManager, ColorManager
from animation_manager import AnimationManager
from particle_system import ParticleSystem, MergeEffect

_HERE       = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.dirname(_HERE)
_SOUNDS_DIR = os.path.join(_ROOT, "assets", "sounds")
_IMG_DIR    = os.path.join(_ROOT, "assets", "images")


# ══════════════════════════════════════════════════════════════════════════
#  SCORE-DRIVEN COLOR SYSTEM
# ══════════════════════════════════════════════════════════════════════════

DARK_SCORE_THEMES = [
    (0,    (0.07,0.04,0.14), (0.12,0.08,0.24), (0.82,0.35,1.00), [0.38,0.10,0.72,1], [0.20,0.12,0.42,1]),
    (100,  (0.04,0.08,0.20), (0.06,0.12,0.30), (0.28,0.68,1.00), [0.10,0.35,0.80,1], [0.08,0.18,0.50,1]),
    (200,  (0.04,0.14,0.08), (0.06,0.20,0.12), (0.15,0.90,0.50), [0.08,0.55,0.32,1], [0.05,0.28,0.18,1]),
    (300,  (0.14,0.12,0.02), (0.22,0.20,0.04), (0.95,0.88,0.18), [0.60,0.50,0.05,1], [0.34,0.28,0.03,1]),
    (400,  (0.16,0.07,0.02), (0.24,0.10,0.03), (1.00,0.58,0.08), [0.72,0.32,0.04,1], [0.40,0.17,0.02,1]),
    (500,  (0.16,0.03,0.03), (0.24,0.05,0.05), (1.00,0.22,0.22), [0.72,0.08,0.08,1], [0.40,0.04,0.04,1]),
    (600,  (0.10,0.02,0.16), (0.16,0.04,0.26), (0.92,0.18,0.88), [0.55,0.06,0.62,1], [0.30,0.04,0.36,1]),
    (700,  (0.02,0.12,0.16), (0.04,0.18,0.26), (0.08,0.88,0.95), [0.04,0.52,0.68,1], [0.02,0.28,0.40,1]),
    (800,  (0.10,0.04,0.18), (0.16,0.06,0.28), (0.72,0.42,1.00), [0.45,0.16,0.78,1], [0.24,0.09,0.44,1]),
    (900,  (0.14,0.09,0.02), (0.22,0.14,0.03), (1.00,0.72,0.16), [0.68,0.46,0.04,1], [0.38,0.26,0.02,1]),
    (1000, (0.02,0.14,0.13), (0.03,0.22,0.20), (0.08,0.95,0.82), [0.04,0.60,0.55,1], [0.02,0.33,0.30,1]),
    (1500, (0.14,0.02,0.09), (0.22,0.04,0.14), (1.00,0.28,0.68), [0.68,0.08,0.42,1], [0.38,0.04,0.24,1]),
    (2048, (0.12,0.10,0.01), (0.20,0.17,0.02), (1.00,0.90,0.18), [0.70,0.60,0.04,1], [0.40,0.34,0.02,1]),
]

LIGHT_SCORE_THEMES = [
    (0,    (0.92,0.88,0.98), (0.78,0.72,0.90), (0.50,0.18,0.82), [0.55,0.28,0.90,1], [0.68,0.55,0.90,1]),
    (100,  (0.85,0.92,0.98), (0.70,0.80,0.92), (0.12,0.38,0.80), [0.15,0.40,0.82,1], [0.55,0.68,0.92,1]),
    (200,  (0.85,0.96,0.90), (0.70,0.88,0.76), (0.10,0.55,0.32), [0.15,0.58,0.36,1], [0.55,0.82,0.65,1]),
    (300,  (0.98,0.96,0.82), (0.90,0.88,0.68), (0.58,0.48,0.04), [0.62,0.52,0.06,1], [0.85,0.78,0.40,1]),
    (400,  (0.99,0.92,0.82), (0.92,0.80,0.65), (0.72,0.32,0.04), [0.78,0.36,0.06,1], [0.94,0.72,0.48,1]),
    (500,  (0.99,0.86,0.86), (0.92,0.72,0.72), (0.72,0.08,0.08), [0.78,0.10,0.10,1], [0.94,0.55,0.55,1]),
    (600,  (0.96,0.86,0.98), (0.86,0.72,0.92), (0.60,0.08,0.68), [0.65,0.10,0.75,1], [0.84,0.55,0.90,1]),
    (700,  (0.84,0.96,0.98), (0.68,0.88,0.92), (0.04,0.55,0.68), [0.06,0.58,0.72,1], [0.48,0.84,0.90,1]),
    (800,  (0.90,0.86,0.99), (0.78,0.72,0.94), (0.42,0.14,0.80), [0.48,0.18,0.84,1], [0.72,0.58,0.94,1]),
    (900,  (0.99,0.96,0.82), (0.94,0.88,0.65), (0.62,0.44,0.02), [0.68,0.48,0.04,1], [0.88,0.78,0.38,1]),
    (1000, (0.82,0.98,0.96), (0.65,0.92,0.88), (0.04,0.58,0.52), [0.06,0.62,0.56,1], [0.44,0.86,0.82,1]),
    (1500, (0.99,0.84,0.92), (0.92,0.68,0.80), (0.68,0.06,0.40), [0.74,0.08,0.44,1], [0.92,0.48,0.70,1]),
    (2048, (0.99,0.97,0.80), (0.94,0.90,0.62), (0.62,0.48,0.02), [0.70,0.56,0.04,1], [0.90,0.82,0.36,1]),
]


def _lerp3(c1, c2, t):
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))

def _lerp4(c1, c2, t):
    return [c1[i] + (c2[i] - c1[i]) * t for i in range(4)]

def _get_theme_lerped(score, theme="dark"):
    entries = DARK_SCORE_THEMES if theme == "dark" else LIGHT_SCORE_THEMES
    for i in range(len(entries) - 1):
        s0, bg0, bd0, ac0, b10, b20 = entries[i]
        s1, bg1, bd1, ac1, b11, b21 = entries[i + 1]
        if s0 <= score < s1:
            t = (score - s0) / max(s1 - s0, 1)
            return (_lerp3(bg0,bg1,t), _lerp3(bd0,bd1,t),
                    _lerp3(ac0,ac1,t), _lerp4(b10,b11,t), _lerp4(b20,b21,t))
    last = entries[-1]
    return (last[1], last[2], last[3], last[4], last[5])


# ══════════════════════════════════════════════════════════════════════════
#  SOUND + MUSIC MANAGER
# ══════════════════════════════════════════════════════════════════════════

class SoundManager:
    """
    Manages sound effects AND background music via Kivy SoundLoader.
    No pygame dependency — works natively on Android.
    """

    SFX_FILES = {
        "move":     "move.wav",
        "merge":    "merge.wav",
        "score":    "score.wav",
        "win":      "win.wav",
        "gameover": "gameover.wav",
    }
    BGM_FILE = "bgm.wav"

    def __init__(self):
        self.sfx_enabled = True
        self.bgm_enabled = True
        self._sfx        = {}
        self._bgm        = None
        self._bgm_vol    = 0.30
        self._sfx_vol    = 0.70
        self._init()

    def _init(self):
        from kivy.core.audio import SoundLoader
        for key, fname in self.SFX_FILES.items():
            path = os.path.join(_SOUNDS_DIR, fname)
            if os.path.exists(path):
                try:
                    snd = SoundLoader.load(path)
                    if snd:
                        snd.volume = self._sfx_vol
                        self._sfx[key] = snd
                except Exception as e:
                    print(f"[Sound] Could not load {fname}: {e}")
        print(f"[Sound] {len(self._sfx)}/{len(self.SFX_FILES)} SFX loaded")
        bgm_path = os.path.join(_SOUNDS_DIR, self.BGM_FILE)
        if os.path.exists(bgm_path):
            try:
                self._bgm = SoundLoader.load(bgm_path)
                if self._bgm:
                    self._bgm.volume = self._bgm_vol
                    self._bgm.loop   = True
                    print(f"[Sound] BGM loaded: {bgm_path}")
            except Exception as e:
                print(f"[Sound] BGM load failed: {e}")
        else:
            print(f"[Sound] BGM file not found: {bgm_path}")

    # ── SFX ───────────────────────────────────────────────────────────────

    def play_sfx(self, key):
        if not self.sfx_enabled:
            return
        snd = self._sfx.get(key)
        if snd:
            try:
                snd.stop()
                snd.play()
            except Exception as e:
                print(f"[Sound] play_sfx({key}) error: {e}")

    def set_sfx_enabled(self, val):
        self.sfx_enabled = bool(val)

    # ── BGM ───────────────────────────────────────────────────────────────

    def start_bgm(self):
        if not self._bgm or not self.bgm_enabled:
            return
        try:
            if self._bgm.state != "play":
                self._bgm.play()
            print("[Sound] BGM started")
        except Exception as e:
            print(f"[Sound] BGM start error: {e}")

    def stop_bgm(self):
        if not self._bgm:
            return
        try:
            self._bgm.stop()
        except Exception:
            pass

    def pause_bgm(self):
        if not self._bgm:
            return
        try:
            self._bgm.stop()
        except Exception:
            pass

    def resume_bgm(self):
        if not self._bgm or not self.bgm_enabled:
            return
        try:
            if self._bgm.state != "play":
                self._bgm.play()
        except Exception:
            pass

    def set_bgm_enabled(self, val):
        was_enabled = self.bgm_enabled
        self.bgm_enabled = bool(val)
        if self.bgm_enabled and not was_enabled:
            self.start_bgm()
        elif not self.bgm_enabled:
            self.stop_bgm()

    def set_bgm_volume(self, vol):
        self._bgm_vol = max(0.0, min(1.0, vol))
        if self._bgm:
            try:
                self._bgm.volume = self._bgm_vol
            except Exception:
                pass

    def reload_settings(self, storage):
        self.set_sfx_enabled(storage.get_setting("sound_enabled", True))
        bgm_on = storage.get_setting("bgm_enabled", True)
        self.bgm_enabled = bool(bgm_on)
        if not bgm_on:
            self.stop_bgm()


# Shared singleton
_sound_mgr = SoundManager()

def get_sound_manager():
    return _sound_mgr


# ══════════════════════════════════════════════════════════════════════════
#  BUTTON HELPER
# ══════════════════════════════════════════════════════════════════════════

def _btn(text, bg, w=dp(105), h=dp(40)):
    return Button(
        text=text, font_size="14sp", bold=True,
        background_normal="", background_color=list(bg),
        size_hint=(None, None), size=(w, h), color=(1, 1, 1, 1),
    )


# ══════════════════════════════════════════════════════════════════════════
#  TILE WIDGET
# ══════════════════════════════════════════════════════════════════════════

class TileWidget(Widget):
    CORNER_RADIUS = dp(14)

    def __init__(self, value=0, theme="dark", **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.theme = theme
        self.bind(size=self._redraw, pos=self._redraw)
        self._redraw()

    def _make_texture(self):
        if self.value == 0:
            return None
        tile_w = self.width if self.width > 0 else dp(80)
        digits = len(str(self.value))
        if digits <= 1:
            fs = tile_w * 0.58
        elif digits == 2:
            fs = tile_w * 0.52
        elif digits == 3:
            fs = tile_w * 0.42
        elif digits == 4:
            fs = tile_w * 0.34
        else:
            fs = tile_w * 0.26
        lbl = CoreLabel(text=str(self.value), font_size=fs, bold=True)
        lbl.refresh()
        return lbl.texture

    def _redraw(self, *args):
        self.canvas.clear()
        r, g, b, a     = ColorManager.get_tile_color(self.value, self.theme)
        tr, tg, tb, ta = ColorManager.get_text_color(self.value, self.theme)
        with self.canvas:
            Color(r, g, b, a)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self.CORNER_RADIUS])
            if self.value != 0:
                tex = self._make_texture()
                if tex:
                    Color(tr, tg, tb, ta)
                    tw, th = tex.size
                    Rectangle(texture=tex,
                               pos=(self.x + (self.width - tw) / 2,
                                    self.y + (self.height - th) / 2),
                               size=(tw, th))

    def set_value(self, value, theme=None):
        self.value = value
        if theme:
            self.theme = theme
        self._redraw()

    def get_center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)


# ══════════════════════════════════════════════════════════════════════════
#  SCORE BOX
# ══════════════════════════════════════════════════════════════════════════

class ScoreBox(Widget):
    def __init__(self, title="SCORE", value=0, theme="dark", **kwargs):
        super().__init__(**kwargs)
        self.theme = theme
        self._color_instr = None
        self._bg   = None
        self._tlbl = None
        self._vlbl = None
        self._build(title, value)
        self.bind(size=self._redraw, pos=self._redraw)

    def _build(self, title, value):
        with self.canvas:
            self._color_instr = Color(0.22, 0.14, 0.42, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        tc = (0.75, 0.60, 0.95, 1)
        vc = (1.0, 1.0, 1.0, 1)
        self._tlbl = Label(text=title, font_size="11sp", bold=True, color=tc,
                           halign="center", valign="middle", size_hint=(None, None))
        self._vlbl = Label(text=str(value), font_size="21sp", bold=True, color=vc,
                           halign="center", valign="middle", size_hint=(None, None))
        self.add_widget(self._tlbl)
        self.add_widget(self._vlbl)

    def _redraw(self, *args):
        if self._bg:
            self._bg.pos  = self.pos
            self._bg.size = self.size
        if self._tlbl:
            self._tlbl.size      = (self.width, dp(18))
            self._tlbl.pos       = (self.x, self.y + self.height * 0.52)
            self._tlbl.text_size = (self.width, dp(18))
        if self._vlbl:
            self._vlbl.size      = (self.width, dp(30))
            self._vlbl.pos       = (self.x, self.y + dp(4))
            self._vlbl.text_size = (self.width, dp(30))

    def tint(self, r, g, b, text_dark=False):
        if self._color_instr:
            self._color_instr.rgb = (r, g, b)
        tc = (0.25, 0.15, 0.45, 1) if text_dark else (0.80, 0.65, 0.95, 1)
        vc = (0.10, 0.05, 0.30, 1) if text_dark else (1.0, 1.0, 1.0, 1)
        if self._tlbl: self._tlbl.color = tc
        if self._vlbl: self._vlbl.color = vc

    def set_value(self, value):
        if self._vlbl:
            self._vlbl.text = str(value)



# ══════════════════════════════════════════════════════════════════════════
#  SCORE MILESTONE WORDS
# ══════════════════════════════════════════════════════════════════════════

SCORE_WORDS = [
    (4,     "Nice!",         (0.70, 0.85, 1.00, 1)),
    (8,     "Good!",         (0.60, 1.00, 0.75, 1)),
    (16,    "Great!",        (1.00, 0.90, 0.30, 1)),
    (32,    "Amazing!",      (1.00, 0.65, 0.20, 1)),
    (64,    "Excellent!",    (1.00, 0.40, 0.40, 1)),
    (128,   "Superb!",       (0.95, 0.30, 0.90, 1)),
    (256,   "Fantastic!",    (0.40, 0.90, 1.00, 1)),
    (512,   "Brilliant!",    (0.50, 1.00, 0.50, 1)),
    (1024,  "Incredible!",   (1.00, 0.80, 0.20, 1)),
    (2048,  "Unstoppable!",  (1.00, 0.45, 0.20, 1)),
    (4096,  "Legendary!",    (1.00, 0.25, 0.50, 1)),
    (8192,  "GODLIKE!",      (1.00, 0.90, 0.10, 1)),
    (16384, "TRANSCENDENT!", (0.20, 1.00, 0.90, 1)),
    (32768, "OMNIPOTENT!",   (1.00, 0.20, 0.80, 1)),
    (65536, "INFINITE!",     (0.90, 0.90, 0.10, 1)),
]

# Cycling colors for scores beyond the defined list
_OVERFLOW_COLORS = [
    (1.00, 0.20, 0.20, 1),
    (0.20, 1.00, 0.20, 1),
    (0.20, 0.20, 1.00, 1),
    (1.00, 1.00, 0.20, 1),
    (1.00, 0.20, 1.00, 1),
    (0.20, 1.00, 1.00, 1),
]


def _get_score_word(score, prev_score):
    """Return word based on points gained in this single move.
    Continues forever — cycles through INFINITE!/BEYOND!/etc for huge scores."""
    gained = score - prev_score
    if gained <= 0:
        return None, None
    result_word, result_color = None, None
    for threshold, word, color in SCORE_WORDS:
        if gained >= threshold:
            result_word, result_color = word, color
    # Beyond the defined list — generate dynamic words that never stop
    if gained >= SCORE_WORDS[-1][0]:
        import math
        tier = int(math.log2(max(gained, 1))) - int(math.log2(SCORE_WORDS[-1][0]))
        dynamic_words = [
            "INFINITE!", "BEYOND!", "COSMIC!", "ETERNAL!", "DIVINE!",
            "MYTHICAL!", "CELESTIAL!", "UNIVERSAL!", "IMMORTAL!", "ABSOLUTE!",
        ]
        result_word  = dynamic_words[tier % len(dynamic_words)]
        result_color = _OVERFLOW_COLORS[tier % len(_OVERFLOW_COLORS)]
    return result_word, result_color


class ScorePopLabel(Widget):
    """Big bold praise word that floats upward and fades out."""

    def __init__(self, text, color, cx, cy, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(320), dp(80))
        self.center_x = cx
        self.center_y = cy
        self.opacity  = 0

        # Shadow label (dark outline effect)
        self._shadow = Label(
            text=text, font_size="50sp", bold=True,
            color=(0, 0, 0, 0.55),
            halign="center", valign="middle",
            size_hint=(None, None), size=(dp(324), dp(84)),
        )
        self._shadow.text_size = (dp(324), dp(84))
        self.add_widget(self._shadow)

        # Main label
        self._lbl = Label(
            text=text, font_size="50sp", bold=True,
            color=color, halign="center", valign="middle",
            size_hint=(None, None), size=(dp(320), dp(80)),
        )
        self._lbl.text_size = (dp(320), dp(80))
        self.add_widget(self._lbl)
        self.bind(pos=self._rel, size=self._rel)
        Clock.schedule_once(self._run, 0.05)

    def _rel(self, *a):
        if self._shadow:
            self._shadow.pos       = (self.x + dp(2), self.y - dp(2))
            self._shadow.size      = (self.width + dp(4), self.height + dp(4))
            self._shadow.text_size = self._shadow.size
        if self._lbl:
            self._lbl.pos       = self.pos
            self._lbl.size      = self.size
            self._lbl.text_size = self.size

    def _run(self, dt):
        start_y = self.y
        # Phase 1: scale up using size (not font_size string)
        anim_in = Animation(
            size=(dp(340), dp(96)),
            opacity=1,
            duration=0.22, t="out_back"
        )
        # Phase 2: float up
        anim_float = Animation(y=start_y + dp(55), opacity=1, duration=0.65, t="out_quad")
        # Phase 3: fade out while continuing up
        anim_fade  = Animation(y=start_y + dp(90), opacity=0, duration=0.50, t="in_quad")

        def _start_float(*a):
            (anim_float + anim_fade).start(self)
            anim_fade.bind(on_complete=lambda *a: self._remove())

        anim_in.bind(on_complete=_start_float)
        anim_in.start(self)

    def _remove(self):
        if self.parent:
            self.parent.remove_widget(self)

# ══════════════════════════════════════════════════════════════════════════
#  GAME BOARD
# ══════════════════════════════════════════════════════════════════════════

class GameBoard(Widget):
    GRID_PADDING    = dp(10)
    TILE_GAP        = dp(8)
    SWIPE_THRESHOLD = dp(35)
    SLIDE_DURATION  = 0.10   # seconds for tile slide animation

    def __init__(self, game_logic, theme="dark",
                 on_move=None, on_game_over=None, on_win=None, **kwargs):
        super().__init__(**kwargs)
        self.logic                  = game_logic
        self.theme                  = theme
        self.on_move_callback       = on_move
        self.on_game_over_callback  = on_game_over
        self.on_win_callback        = on_win
        self.move_count             = 0
        self._animating             = False
        self._touch_start           = None
        self._touch_start_pos       = None
        self.tile_widgets           = [[None] * 4 for _ in range(4)]
        self.particle_sys           = ParticleSystem(self)
        self.merge_effect           = MergeEffect(self.particle_sys)
        self._board_bg              = (0.12, 0.08, 0.24)
        self.bind(size=self._rebuild_board, pos=self._rebuild_board)

    # ── Geometry helpers ──────────────────────────────────────────────────

    def _tile_size(self):
        avail = min(self.width, self.height) - self.GRID_PADDING * 2 - self.TILE_GAP * 3
        return avail / 4

    def _cell_pos(self, row, col):
        """Return pixel (x, y) for board cell (row, col)."""
        ts = self._tile_size()
        x  = self.x + self.GRID_PADDING + col * (ts + self.TILE_GAP)
        y  = self.y + self.GRID_PADDING + (3 - row) * (ts + self.TILE_GAP)
        return x, y

    # ── Board construction ────────────────────────────────────────────────

    def _rebuild_board(self, *args):
        self.canvas.before.clear()
        bb = self._board_bg
        with self.canvas.before:
            Color(bb[0], bb[1], bb[2], 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
        for row in self.tile_widgets:
            for tw in row:
                if tw and tw.parent:
                    self.remove_widget(tw)
        ts = self._tile_size()
        for r in range(4):
            for c in range(4):
                x, y = self._cell_pos(r, c)
                tile = TileWidget(value=self.logic.board[r][c], theme=self.theme,
                                  pos=(x, y), size=(ts, ts))
                self.tile_widgets[r][c] = tile
                self.add_widget(tile)

    def set_board_color(self, rgb):
        self._board_bg = rgb
        self._rebuild_board()

    # ── Animated move ─────────────────────────────────────────────────────

    def _animate_move(self, old_board, new_board, merged_positions, new_tile_pos,
                      had_merge, on_done):
        """
        Dramatic tile slide animation.
        Moving tiles scale up slightly as they travel, then snap back —
        giving a satisfying 'swoosh' feel. Stationary tiles do a subtle pulse.
        """
        dur = self.SLIDE_DURATION
        ts  = self._tile_size()

        target_positions = {}
        for r in range(4):
            for c in range(4):
                target_positions[(r, c)] = self._cell_pos(r, c)

        total_tiles = sum(1 for r in range(4) for c in range(4)
                          if old_board[r][c] != 0)
        if total_tiles == 0:
            on_done()
            return

        pending  = [total_tiles]
        finished = [False]

        def _one_done(*args):
            pending[0] -= 1
            if pending[0] <= 0 and not finished[0]:
                finished[0] = True
                on_done()

        for r in range(4):
            for c in range(4):
                tw = self.tile_widgets[r][c]
                if not tw:
                    _one_done()
                    continue

                new_x, new_y = target_positions[(r, c)]
                dist_x = abs(tw.x - new_x)
                dist_y = abs(tw.y - new_y)
                is_moving = dist_x > 1 or dist_y > 1

                if is_moving:
                    # Scale up slightly while sliding, like the tile is "lifting"
                    lift   = ts * 0.12          # extra size during travel
                    offset = lift / 2           # centre compensation

                    # Phase 1: grow + slide simultaneously
                    travel = Animation(
                        x=new_x - offset,
                        y=new_y - offset,
                        width=ts + lift,
                        height=ts + lift,
                        duration=dur * 0.80,
                        t="out_expo",           # very fast start, quick deceleration
                    )
                    # Phase 2: snap back to exact size
                    land = Animation(
                        x=new_x, y=new_y,
                        width=ts, height=ts,
                        duration=dur * 0.20,
                        t="out_back",           # tiny bounce on landing
                    )
                    seq = travel + land
                    seq.bind(on_complete=_one_done)
                    seq.start(tw)
                else:
                    # Stationary tile — tiny pulse so there's visual activity
                    pulse = (
                        Animation(width=ts*1.05, height=ts*1.05,
                                  x=tw.x - ts*0.025, y=tw.y - ts*0.025,
                                  duration=dur * 0.35, t="out_quad") +
                        Animation(width=ts, height=ts,
                                  x=tw.x, y=tw.y,
                                  duration=dur * 0.35, t="in_quad")
                    )
                    pulse.bind(on_complete=_one_done)
                    pulse.start(tw)

    def _apply_after_slide(self, merged_positions, new_tile_pos):
        """Called after slide animations finish — update tile values and effects."""
        ts = self._tile_size()
        for r in range(4):
            for c in range(4):
                tw = self.tile_widgets[r][c]
                if not tw:
                    continue
                # Snap position (in case of float drift)
                nx, ny = self._cell_pos(r, c)
                tw.pos = (nx, ny)
                tw.size = (ts, ts)

                nv = self.logic.board[r][c]
                tw.set_value(nv, self.theme)

                if merged_positions and (r, c) in merged_positions and nv > 0:
                    AnimationManager.merge_tile(tw)
                    color = ColorManager.get_tile_color(nv, self.theme)
                    cx, cy = tw.get_center()
                    self.merge_effect.play(cx, cy, color, value=nv)

        # Spawn new tile
        if new_tile_pos:
            r, c = new_tile_pos
            tw = self.tile_widgets[r][c]
            if tw:
                AnimationManager.spawn_tile(tw)

    # ── Touch input ────────────────────────────────────────────────────────

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_start     = touch.id
            self._touch_start_pos = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.id != self._touch_start:
            return super().on_touch_up(touch)
        self._touch_start = None
        if self._touch_start_pos is None or self._animating:
            return True
        dx = touch.pos[0] - self._touch_start_pos[0]
        dy = touch.pos[1] - self._touch_start_pos[1]
        self._touch_start_pos = None
        if abs(dx) < self.SWIPE_THRESHOLD and abs(dy) < self.SWIPE_THRESHOLD:
            return True
        direction = ("right" if dx > 0 else "left") if abs(dx) > abs(dy) \
                    else ("up" if dy > 0 else "down")
        self._handle_move(direction)
        return True

    def _handle_move(self, direction):
        if self._animating:
            return

        # Capture board state BEFORE the move
        import copy
        old_board = copy.deepcopy(self.logic.board)

        fn = {"left": self.logic.move_left,  "right": self.logic.move_right,
              "up":   self.logic.move_up,    "down":  self.logic.move_down}[direction]
        moved = fn()

        if moved:
            self.move_count += 1
            self._animating = True
            had_merge        = bool(self.logic.merged_positions)
            merged_positions = list(self.logic.merged_positions)
            new_tile_pos     = self.logic.new_tile_pos

            # Temporarily hide the new tile during slide
            if new_tile_pos:
                r, c = new_tile_pos
                tw = self.tile_widgets[r][c]
                if tw:
                    tw.opacity = 0

            # Update all tile GRAPHICS to new values immediately
            # but keep positions at old grid spots for the slide
            # We need to restore old positions first, then slide to new
            for r in range(4):
                for c in range(4):
                    tw = self.tile_widgets[r][c]
                    if tw:
                        # Snap to old board position (already there, just ensure)
                        ox, oy = self._cell_pos(r, c)
                        tw.pos = (ox, oy)

            def _after_slide():
                self._apply_after_slide(merged_positions, new_tile_pos)
                # Reveal the new tile
                if new_tile_pos:
                    r2, c2 = new_tile_pos
                    tw2 = self.tile_widgets[r2][c2]
                    if tw2:
                        tw2.opacity = 1
                get_sound_manager().play_sfx("merge" if had_merge else "move")
                if self.on_move_callback:
                    self.on_move_callback(self.logic.score)
                Clock.schedule_once(
                    lambda dt: setattr(self, "_animating", False),
                    0.05)
                Clock.schedule_once(self._check_state, self.SLIDE_DURATION + 0.15)

            self._animate_move(
                old_board=old_board,
                new_board=self.logic.board,
                merged_positions=merged_positions,
                new_tile_pos=new_tile_pos,
                had_merge=had_merge,
                on_done=_after_slide,
            )
        else:
            AnimationManager.shake(self)

    def _check_state(self, dt):
        if self.logic.has_won():
            get_sound_manager().play_sfx("win")
            if self.on_win_callback:
                self.on_win_callback(self.logic.score)
        elif self.logic.is_game_over():
            get_sound_manager().play_sfx("gameover")
            if self.on_game_over_callback:
                self.on_game_over_callback(self.logic.score)

    def do_undo(self):
        self.logic.undo()
        # Rebuild board to show previous state (no slide animation for undo)
        self._rebuild_board()
        if self.on_move_callback:
            self.on_move_callback(self.logic.score)

    def set_theme(self, theme):
        self.theme = theme
        self._rebuild_board()

    def handle_keyboard(self, key):
        if key in ("left", "right", "up", "down"):
            self._handle_move(key)


# ══════════════════════════════════════════════════════════════════════════
#  GAME SCREEN
# ══════════════════════════════════════════════════════════════════════════

class GameScreen(FloatLayout):

    def __init__(self, on_settings=None, on_game_over=None, on_win=None, on_home=None, **kwargs):
        super().__init__(**kwargs)
        self.on_settings_callback  = on_settings
        self.on_game_over_callback = on_game_over
        self.on_win_callback       = on_win
        self.on_home_callback      = on_home
        self.storage = StorageManager()
        self.theme   = self.storage.get_setting("theme", "dark")
        self.logic   = GameLogic()
        self._bg_color_instr = None
        self._bg_rect        = None
        self._prev_score     = 0
        self._game_counted  = False  # prevent double-counting games
        # Ensure _moves_base is initialised in storage
        Clock.schedule_once(self._init_moves_base, 0)
        self._setup_ui()
        self._setup_keyboard()
        Clock.schedule_once(lambda dt: self._apply_score_theme(0, animate=False), 0.05)

    def _start_bgm(self):
        sm = get_sound_manager()
        sm.set_bgm_enabled(self.storage.get_setting("bgm_enabled", True))
        sm.set_sfx_enabled(self.storage.get_setting("sound_enabled", True))

    def _setup_ui(self):
        start_bg = (0.07, 0.04, 0.14, 1) if self.theme == "dark" else (0.92, 0.88, 0.98, 1)
        with self.canvas.before:
            self._bg_color_instr = Color(*start_bg)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)
        self._build_header()
        self._build_board()

    def _build_header(self):
        self.title_label = Label(
            text="Zad 2048", font_size="28sp", bold=True,
            color=(0.82, 0.35, 1.00, 1),
            halign="center", valign="middle",
            size_hint=(None, None), size=(dp(200), dp(44)),
        )
        self.add_widget(self.title_label)

        best = self.storage.get_best_score()
        self.score_box = ScoreBox(title="SCORE", value=0,    theme=self.theme,
                                  size_hint=(None, None), size=(dp(95), dp(52)))
        self.best_box  = ScoreBox(title="BEST",  value=best, theme=self.theme,
                                  size_hint=(None, None), size=(dp(95), dp(52)))
        self.add_widget(self.score_box)
        self.add_widget(self.best_box)

        self.new_game_btn = _btn("New Game", [0.38, 0.10, 0.72, 1])
        self.undo_btn     = _btn("Undo",     [0.20, 0.12, 0.42, 1])
        self.settings_btn = _btn("Settings", [0.20, 0.12, 0.42, 1])

        self.new_game_btn.bind(on_press=self._on_new_game)
        self.undo_btn.bind(on_press=self._on_undo)
        self.settings_btn.bind(on_press=self._on_settings)

        # Home icon button
        home_icon_path = os.path.join(_ROOT, "assets", "images", "home_icon.png")
        self.home_btn = Button(
            background_normal=home_icon_path,
            background_down=home_icon_path,
            background_color=(1, 1, 1, 1),
            border=(0, 0, 0, 0),
            size_hint=(None, None), size=(dp(42), dp(42)),
        )
        self.home_btn.bind(on_press=self._on_home)
        self.add_widget(self.home_btn)

        for w in (self.new_game_btn, self.undo_btn, self.settings_btn):
            self.add_widget(w)

        self.bind(size=self._layout_header, pos=self._layout_header)

    def _build_board(self):
        self.board_widget = GameBoard(
            game_logic=self.logic, theme=self.theme,
            on_move=self._on_score_update,
            on_game_over=self._on_game_over,
            on_win=self._on_win,
            size_hint=(None, None),
        )
        self.add_widget(self.board_widget)
        self.bind(size=self._layout_board, pos=self._layout_board)

    def _layout_header(self, *args):
        w, h = self.size
        px, py = self.pos
        cx = px + w / 2
        m  = dp(10)   # side margin

        # ── Row 1: home | title | score | best  (top of screen) ──────────
        row1_h = dp(50)
        row1_y = py + h - dp(8) - row1_h   # 8dp from top edge

        # Home icon — left
        icon_sz = dp(44)
        self.home_btn.size = (icon_sz, icon_sz)
        self.home_btn.pos  = (px + m, row1_y + (row1_h - icon_sz) / 2)

        # Score boxes — right, fixed width
        box_w, box_h = dp(90), dp(48)
        self.best_box.size  = (box_w, box_h)
        self.score_box.size = (box_w, box_h)
        self.best_box.pos   = (px + w - m - box_w,            row1_y + (row1_h - box_h) / 2)
        self.score_box.pos  = (px + w - m - box_w*2 - dp(6),  row1_y + (row1_h - box_h) / 2)

        # Title — fills remaining space between home btn and score boxes
        title_x = px + m + icon_sz + dp(6)
        title_w = self.score_box.x - title_x - dp(4)
        self.title_label.size      = (title_w, row1_h)
        self.title_label.font_size = "22sp"
        self.title_label.pos       = (title_x, row1_y)
        self.title_label.text_size = (title_w, row1_h)

        # ── Row 2: buttons (below row 1) ──────────────────────────────────
        gap      = dp(7)
        btn_h    = dp(42)
        btn_w    = (w - m * 2 - gap * 2) / 3
        row2_y   = row1_y - dp(8) - btn_h   # 8dp gap between rows

        self.new_game_btn.size = (btn_w, btn_h)
        self.undo_btn.size     = (btn_w, btn_h)
        self.settings_btn.size = (btn_w, btn_h)

        self.new_game_btn.pos = (px + m,                    row2_y)
        self.undo_btn.pos     = (px + m + btn_w + gap,      row2_y)
        self.settings_btn.pos = (px + m + (btn_w + gap)*2,  row2_y)

    def _layout_board(self, *args):
        w, h       = self.size
        # total header height: 8 + 50 + 8 + 42 + 10 bottom gap
        header_h   = dp(8 + 50 + 8 + 42 + 10)
        bottom_pad = dp(10)
        side_pad   = dp(10)
        avail_h    = h - header_h - bottom_pad
        avail_w    = w - side_pad * 2
        board_size = min(avail_w, avail_h)
        self.board_widget.size = (board_size, board_size)
        self.board_widget.pos  = (
            self.x + (w - board_size) / 2,
            self.y + bottom_pad + (avail_h - board_size) / 2,
        )

    def _apply_score_theme(self, score, animate=True):
        bg_rgb, board_rgb, acc_rgb, btn1, btn2 = _get_theme_lerped(score, self.theme)
        is_light = (self.theme == "light")

        if animate:
            Animation(r=bg_rgb[0], g=bg_rgb[1], b=bg_rgb[2],
                      duration=0.7, t="out_quad").start(self._bg_color_instr)
        else:
            self._bg_color_instr.rgb = bg_rgb

        self.title_label.color = (*acc_rgb, 1)
        self.board_widget.set_board_color(board_rgb)
        self.new_game_btn.background_color = btn1
        self.undo_btn.background_color     = btn2
        self.settings_btn.background_color = btn2

        box_r = min(bg_rgb[0]+0.10,1) if not is_light else max(bg_rgb[0]-0.10,0)
        box_g = min(bg_rgb[1]+0.06,1) if not is_light else max(bg_rgb[1]-0.06,0)
        box_b = min(bg_rgb[2]+0.18,1) if not is_light else max(bg_rgb[2]-0.06,0)
        self.score_box.tint(box_r, box_g, box_b, text_dark=is_light)
        self.best_box.tint(box_r, box_g, box_b, text_dark=is_light)

    def _update_bg(self, *args):
        self._bg_rect.pos  = self.pos
        self._bg_rect.size = self.size

    def _setup_keyboard(self):
        Window.bind(on_keyboard=self._on_keyboard)

    def _on_keyboard(self, window, key, *args):
        km = {273: "up", 274: "down", 275: "right", 276: "left"}
        if key in km:
            self.board_widget.handle_keyboard(km[key])
            return True
        return False

    def _on_score_update(self, score):
        self.score_box.set_value(score)
        # Persist all stats continuously so Settings always shows current values
        stats = self.storage.get_stats()
        changed = False
        if score > stats.get("best_score", 0):
            stats["best_score"] = score
            self.best_box.set_value(score)
            changed = True
        tile = self.logic.get_highest_tile()
        if tile > stats.get("highest_tile", 0):
            stats["highest_tile"] = tile
            changed = True
        # Always keep total_moves up to date — add current session moves to stored total
        stored_base = stats.get("_moves_base", 0)
        stats["total_moves"] = stored_base + self.board_widget.move_count
        changed = True
        if changed:
            self.storage.save_stats(stats)
        self._apply_score_theme(score, animate=True)
        word, color = _get_score_word(score, self._prev_score)
        if word:
            pop = ScorePopLabel(text=word, color=color,
                                cx=self.center_x,
                                cy=self.center_y + dp(130))
            self.add_widget(pop)
        self._prev_score = score

    def _on_new_game(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(lambda dt: self._start_new_game(), 0.18)

    def _on_undo(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(lambda dt: self.board_widget.do_undo(), 0.1)

    def _on_home(self, btn):
        AnimationManager.button_press(btn)
        self._save_game_state()
        self._save_stats(self.logic.score, count_game=False)
        stats = self.storage.get_stats()
        stats["_moves_base"] = stats.get("total_moves", 0)
        self.storage.save_stats(stats)
        Clock.schedule_once(
            lambda dt: self.on_home_callback() if hasattr(self, "on_home_callback") and self.on_home_callback else None, 0.18)

    def _save_game_state(self):
        """Save current board and score so the game can be resumed."""
        try:
            import json
            state = {
                "board": self.logic.board,
                "score": self.logic.score,
                "in_progress": True,
            }
            self.storage.set_setting("saved_game", json.dumps(state))
        except Exception as e:
            print(f"[Game] Failed to save game state: {e}")

    def _load_game_state(self):
        """Restore saved game state if one exists. Returns True if restored."""
        try:
            import json
            raw = self.storage.get_setting("saved_game", None)
            if not raw:
                return False
            state = json.loads(raw)
            if not state.get("in_progress"):
                return False
            self.logic.board = state["board"]
            self.logic.score = state["score"]
            return True
        except Exception as e:
            print(f"[Game] Failed to load game state: {e}")
            return False

    def _clear_game_state(self):
        """Clear saved game state (called on new game or game over)."""
        self.storage.set_setting("saved_game", None)

    def _on_settings(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(
            lambda dt: self.on_settings_callback() if self.on_settings_callback else None, 0.15)

    def _on_game_over(self, score):
        self._clear_game_state()
        self._save_stats(score)
        if self.on_game_over_callback:
            self.on_game_over_callback(score)

    def _on_win(self, score):
        if self.on_win_callback:
            self.on_win_callback(score)

    def _save_stats(self, score, count_game=True):
        """
        Persist end-of-game stats.
        count_game=True  → increments total_games (game over / home button)
        count_game=False → only saves score/tile (new game restart, no double-count)
        """
        stats = self.storage.get_stats()
        if count_game and not self._game_counted:
            stats["total_games"] += 1
            self._game_counted = True
        if score > stats.get("best_score", 0):
            stats["best_score"] = score
        tile = self.logic.get_highest_tile()
        if tile > stats.get("highest_tile", 0):
            stats["highest_tile"] = tile
        self.storage.save_stats(stats)

    def _start_new_game(self):
        if not self._game_counted:
            self._save_stats(self.logic.score, count_game=True)
        else:
            self._save_stats(self.logic.score, count_game=False)
        self._game_counted = False
        self._clear_game_state()
        stats = self.storage.get_stats()
        stats["_moves_base"] = stats.get("total_moves", 0)
        self.storage.save_stats(stats)
        self.logic.reset()
        self.board_widget.move_count = 0
        self.board_widget._rebuild_board()
        self.score_box.set_value(0)
        self.best_box.set_value(self.storage.get_best_score())
        self._apply_score_theme(0, animate=True)
        self._prev_score = 0

    def _init_moves_base(self, dt):
        """Set _moves_base in storage so move_count always adds on top correctly."""
        stats = self.storage.get_stats()
        if "_moves_base" not in stats:
            stats["_moves_base"] = stats.get("total_moves", 0)
            self.storage.save_stats(stats)

    def refresh_theme(self):
        self.theme = self.storage.get_setting("theme", "dark")
        self.board_widget.set_theme(self.theme)
        get_sound_manager().reload_settings(self.storage)
        self._apply_score_theme(self.logic.score, animate=False)

    def on_enter(self):
        sm = get_sound_manager()
        sm.set_sfx_enabled(self.storage.get_setting("sound_enabled", True))
        bgm_on = self.storage.get_setting("bgm_enabled", True)
        sm.bgm_enabled = bgm_on
        if not bgm_on:
            sm.stop_bgm()
        # Only restore from storage if there is no active game in memory
        # (i.e. board is empty — fresh start or first launch)
        board_empty = all(
            self.logic.board[r][c] == 0
            for r in range(4) for c in range(4)
        )
        if board_empty and self._load_game_state():
            self.board_widget._rebuild_board()
            self.score_box.set_value(self.logic.score)
            self.best_box.set_value(self.storage.get_best_score())
            self._apply_score_theme(self.logic.score, animate=False)
            self._prev_score = self.logic.score
            print("[Game] Resumed saved game")
        elif not board_empty:
            # Game already in memory — just refresh visuals
            self.board_widget._rebuild_board()
            self.score_box.set_value(self.logic.score)
            self.best_box.set_value(self.storage.get_best_score())
            self._apply_score_theme(self.logic.score, animate=False)

    def on_leave(self):
        get_sound_manager().pause_bgm()
