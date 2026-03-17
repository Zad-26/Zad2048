"""
Zad 2048 - Animation Manager
Rich animations: slide, merge-crash, spawn-bounce, shake, score-pop,
number-pop, and the new tile-crash effect when merging.
"""

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
import math, random


class AnimationManager:

    SLIDE_DURATION  = 0.10
    MERGE_DURATION  = 0.22
    SPAWN_DURATION  = 0.25
    FADE_DURATION   = 0.30
    CRASH_DURATION  = 0.28

    @staticmethod
    def slide_tile(widget, target_x, target_y, on_complete=None):
        anim = Animation(x=target_x, y=target_y,
                         duration=AnimationManager.SLIDE_DURATION, t="out_cubic")
        if on_complete:
            anim.bind(on_complete=lambda *a: on_complete())
        anim.start(widget)
        return anim

    # ── MERGE / CRASH ANIMATION ───────────────────────────────────────────
    @staticmethod
    def merge_tile(widget, on_complete=None):
        """
        Multi-stage crash-merge animation:
        1. Quick squash (wider, shorter)  — impact frame
        2. Overshoot scale-up            — explosion
        3. Settle back to normal         — with slight wobble
        """
        ow, oh = widget.size[0], widget.size[1]
        ox, oy = widget.pos[0], widget.pos[1]

        # Stage 1: squash — tile "impacts"
        squash = Animation(
            size=(ow * 1.30, oh * 0.82),
            pos=(ox - ow*0.15, oy + oh*0.09),
            duration=AnimationManager.CRASH_DURATION * 0.20,
            t="out_quad",
        )
        # Stage 2: explode outward
        explode = Animation(
            size=(ow * 1.22, oh * 1.22),
            pos=(ox - ow*0.11, oy - oh*0.11),
            duration=AnimationManager.CRASH_DURATION * 0.35,
            t="out_cubic",
        )
        # Stage 3: settle with back-ease (slight overshoot)
        settle = Animation(
            size=(ow, oh),
            pos=(ox, oy),
            duration=AnimationManager.CRASH_DURATION * 0.45,
            t="out_back",
        )
        seq = squash + explode + settle
        if on_complete:
            seq.bind(on_complete=lambda *a: on_complete())
        seq.start(widget)
        return seq

    # ── SPAWN ANIMATION ───────────────────────────────────────────────────
    @staticmethod
    def spawn_tile(widget, on_complete=None):
        """
        Tile appears with a dramatic pop:
        1. Start tiny + rotated feel (scale from 0)
        2. Overshoot to 115%
        3. Settle to 100%
        """
        ow, oh = widget.size[0], widget.size[1]
        ox, oy = widget.pos[0], widget.pos[1]

        widget.size    = (0, 0)
        widget.pos     = (ox + ow/2, oy + oh/2)
        widget.opacity = 0

        pop = Animation(
            size=(ow * 1.18, oh * 1.18),
            pos=(ox - ow*0.09, oy - oh*0.09),
            opacity=1,
            duration=AnimationManager.SPAWN_DURATION * 0.55,
            t="out_cubic",
        )
        settle = Animation(
            size=(ow, oh),
            pos=(ox, oy),
            duration=AnimationManager.SPAWN_DURATION * 0.45,
            t="out_back",
        )
        seq = pop + settle
        if on_complete:
            seq.bind(on_complete=lambda *a: on_complete())
        seq.start(widget)
        return seq

    # ── NUMBER POP (score label flash) ────────────────────────────────────
    @staticmethod
    def number_pop(label, scale=1.45, color_flash=(1, 0.9, 0.2, 1), on_complete=None):
        """
        Label quickly scales up with a colour flash, then returns.
        Used when score increases or a tile number changes.
        """
        orig_fs = label.font_size
        orig_col = label.color[:]

        flash_up = Animation(
            font_size=orig_fs * scale,
            duration=0.10, t="out_cubic"
        )
        flash_up.bind(on_start=lambda *a: setattr(label, "color", color_flash))

        restore = Animation(
            font_size=orig_fs,
            duration=0.15, t="in_quad"
        )
        restore.bind(on_complete=lambda *a: setattr(label, "color", orig_col))

        seq = flash_up + restore
        if on_complete:
            seq.bind(on_complete=lambda *a: on_complete())
        seq.start(label)
        return seq

    # ── SHAKE (invalid move / game over) ──────────────────────────────────
    @staticmethod
    def shake(widget, intensity=dp(9), on_complete=None):
        ox = widget.x
        seq = (
            Animation(x=ox + intensity,  duration=0.04, t="linear") +
            Animation(x=ox - intensity,  duration=0.04, t="linear") +
            Animation(x=ox + intensity*0.6, duration=0.04, t="linear") +
            Animation(x=ox - intensity*0.6, duration=0.04, t="linear") +
            Animation(x=ox,              duration=0.04, t="linear")
        )
        if on_complete:
            seq.bind(on_complete=lambda *a: on_complete())
        seq.start(widget)
        return seq

    # ── FADE IN / OUT ─────────────────────────────────────────────────────
    @staticmethod
    def fade_in(widget, duration=None, on_complete=None):
        d = duration or AnimationManager.FADE_DURATION
        widget.opacity = 0
        anim = Animation(opacity=1, duration=d, t="out_quad")
        if on_complete:
            anim.bind(on_complete=lambda *a: on_complete())
        anim.start(widget)
        return anim

    @staticmethod
    def fade_out(widget, duration=None, on_complete=None):
        d = duration or AnimationManager.FADE_DURATION
        anim = Animation(opacity=0, duration=d, t="in_quad")
        if on_complete:
            anim.bind(on_complete=lambda *a: on_complete())
        anim.start(widget)
        return anim

    # ── BUTTON PRESS ──────────────────────────────────────────────────────
    @staticmethod
    def button_press(widget, on_complete=None):
        ow, oh = widget.size[0], widget.size[1]
        ox, oy = widget.pos[0], widget.pos[1]
        shrink = Animation(
            size=(ow*0.91, oh*0.91),
            pos=(ox + ow*0.045, oy + oh*0.045),
            duration=0.07, t="out_quad",
        )
        restore = Animation(
            size=(ow, oh), pos=(ox, oy),
            duration=0.12, t="out_back",
        )
        seq = shrink + restore
        if on_complete:
            seq.bind(on_complete=lambda *a: on_complete())
        seq.start(widget)
        return seq

    # ── PULSE (for 2048 tile glow) ────────────────────────────────────────
    @staticmethod
    def pulse(widget, scale=1.06, duration=0.9):
        ow, oh = widget.size[0], widget.size[1]
        ox, oy = widget.pos[0], widget.pos[1]
        grow = Animation(
            size=(ow*scale, oh*scale),
            pos=(ox - ow*(scale-1)/2, oy - oh*(scale-1)/2),
            duration=duration/2, t="in_out_sine",
        )
        shrink = Animation(
            size=(ow, oh), pos=(ox, oy),
            duration=duration/2, t="in_out_sine",
        )
        anim = grow + shrink
        anim.repeat = True
        anim.start(widget)
        return anim

    # ── SCREEN SLIDE ──────────────────────────────────────────────────────
    @staticmethod
    def slide_in_from_bottom(widget, on_complete=None):
        from kivy.core.window import Window
        widget.y = -Window.height
        widget.opacity = 1
        anim = Animation(y=0, duration=0.38, t="out_cubic")
        if on_complete:
            anim.bind(on_complete=lambda *a: on_complete())
        anim.start(widget)
        return anim


class GradientAnimator:
    """Animated shifting background gradient."""

    LIGHT_STOPS = [
        (0.96, 0.88, 0.92), (0.88, 0.92, 0.98),
        (0.98, 0.96, 0.85), (0.90, 0.96, 0.90),
    ]
    DARK_STOPS = [
        (0.10, 0.05, 0.20), (0.05, 0.08, 0.22),
        (0.15, 0.05, 0.25), (0.08, 0.05, 0.18),
    ]

    def __init__(self, callback, theme="dark", speed=0.003):
        self.callback = callback
        self.theme    = theme
        self.speed    = speed
        self.t        = 0.0
        self._event   = None

    def start(self):
        self._event = Clock.schedule_interval(self._update, 1/30)

    def stop(self):
        if self._event:
            self._event.cancel()
            self._event = None

    def set_theme(self, theme):
        self.theme = theme

    def _lerp(self, a, b, t):
        return a + (b - a) * t

    def _update(self, dt):
        self.t = (self.t + self.speed) % 1.0
        stops = self.DARK_STOPS if self.theme == "dark" else self.LIGHT_STOPS
        n = len(stops)
        scaled = self.t * n
        idx = int(scaled) % n
        nxt = (idx + 1) % n
        lt  = scaled - int(scaled)
        c1, c2 = stops[idx], stops[nxt]
        r = self._lerp(c1[0], c2[0], lt)
        g = self._lerp(c1[1], c2[1], lt)
        b = self._lerp(c1[2], c2[2], lt)
        self.callback(r, g, b)