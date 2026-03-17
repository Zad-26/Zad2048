"""
Zad 2048 - Enhanced Particle System
Dramatic merge effects: spark burst, shockwave ring, and floating score numbers.
"""

import random, math
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.text import Label as CoreLabel


# ══════════════════════════════════════════════════════════════════════════
#  SPARK PARTICLE
# ══════════════════════════════════════════════════════════════════════════

class Spark:
    """A single flying spark particle."""

    def __init__(self, canvas, x, y, color_rgba, size=None):
        self.canvas = canvas
        self.x  = x
        self.y  = y
        self.r, self.g, self.b, _ = color_rgba
        self.radius = size or random.uniform(dp(2.5), dp(6))
        self.alive  = True
        self.life   = 1.0
        self.decay  = random.uniform(2.2, 4.5)

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(dp(60), dp(180))
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = -dp(120)  # pulls sparks downward

        with self.canvas:
            self._ci = Color(self.r, self.g, self.b, 1.0)
            self._el = Ellipse(
                pos=(self.x - self.radius, self.y - self.radius),
                size=(self.radius * 2, self.radius * 2),
            )

    def update(self, dt):
        if not self.alive:
            return
        self.life -= self.decay * dt
        if self.life <= 0:
            self.life  = 0
            self.alive = False
        self.vx  *= 0.88
        self.vy  *= 0.88
        self.vy  += self.gravity * dt
        self.x   += self.vx * dt
        self.y   += self.vy * dt
        self._ci.a = max(0, self.life)
        self._el.pos  = (self.x - self.radius, self.y - self.radius)
        self._el.size = (self.radius * 2, self.radius * 2)

    def remove(self):
        try:
            self.canvas.remove(self._ci)
            self.canvas.remove(self._el)
        except Exception:
            pass
        self.alive = False


# ══════════════════════════════════════════════════════════════════════════
#  SHOCKWAVE RING
# ══════════════════════════════════════════════════════════════════════════

class ShockwaveRing:
    """Expanding ring that fades — gives a satisfying 'impact' feel."""

    def __init__(self, canvas, x, y, color_rgba):
        self.canvas = canvas
        self.x, self.y = x, y
        self.r, self.g, self.b, _ = color_rgba
        self.radius = dp(8)
        self.max_r  = dp(55)
        self.alive  = True
        self.life   = 1.0
        self.speed  = 3.5  # life lost per second

        with self.canvas:
            self._ci   = Color(self.r, self.g, self.b, 0.9)
            self._ring = Line(
                circle=(self.x, self.y, self.radius),
                width=dp(2.5),
            )

    def update(self, dt):
        if not self.alive:
            return
        self.life -= self.speed * dt
        if self.life <= 0:
            self.life  = 0
            self.alive = False
        self.radius = dp(8) + (self.max_r - dp(8)) * (1 - self.life)
        self._ci.a   = max(0, self.life * 0.85)
        self._ring.circle = (self.x, self.y, self.radius)

    def remove(self):
        try:
            self.canvas.remove(self._ci)
            self.canvas.remove(self._ring)
        except Exception:
            pass
        self.alive = False


# ══════════════════════════════════════════════════════════════════════════
#  FLOATING SCORE NUMBER
# ══════════════════════════════════════════════════════════════════════════

class FloatingNumber:
    """A '+N' label that floats upward and fades — shows merge value."""

    def __init__(self, parent_widget, x, y, value, color_rgba):
        self.parent = parent_widget
        self.alive  = True
        self.life   = 1.0
        self.vy     = dp(65)
        self.y_pos  = y

        r, g, b, _ = color_rgba
        # Make text bright
        text_r = min(r * 1.4, 1.0)
        text_g = min(g * 1.4, 1.0)
        text_b = min(b * 1.4, 1.0)

        self._label = Label(
            text=f"+{value}",
            font_size="22sp",
            bold=True,
            color=(text_r, text_g, text_b, 1.0),
            size_hint=(None, None),
            size=(dp(80), dp(36)),
        )
        self._label.center_x = x
        self._label.y        = y
        parent_widget.add_widget(self._label)

    def update(self, dt):
        if not self.alive:
            return
        self.life  -= 2.2 * dt
        self.y_pos += self.vy * dt
        self.vy    *= 0.96
        if self.life <= 0:
            self.life  = 0
            self.alive = False
        self._label.y       = self.y_pos
        self._label.opacity = max(0, self.life)

    def remove(self):
        try:
            if self._label.parent:
                self.parent.remove_widget(self._label)
        except Exception:
            pass
        self.alive = False


# ══════════════════════════════════════════════════════════════════════════
#  PARTICLE SYSTEM
# ══════════════════════════════════════════════════════════════════════════

class ParticleSystem:

    SPARK_COUNT = 16

    def __init__(self, parent_widget: Widget):
        self.parent    = parent_widget
        self.sparks    = []
        self.rings     = []
        self.floaters  = []
        self._event    = None

    def burst(self, x, y, color_rgba, value=None):
        """
        Full merge effect at (x, y):
          - Spark explosion
          - Shockwave ring
          - Floating +value number
        """
        # Sparks
        for _ in range(self.SPARK_COUNT):
            self.sparks.append(Spark(self.parent.canvas, x, y, color_rgba))

        # Larger sparks for emphasis
        for _ in range(5):
            self.sparks.append(
                Spark(self.parent.canvas, x, y, color_rgba,
                      size=random.uniform(dp(4), dp(9)))
            )

        # Shockwave ring
        self.rings.append(ShockwaveRing(self.parent.canvas, x, y, color_rgba))
        # Second delayed ring
        Clock.schedule_once(
            lambda dt: self.rings.append(
                ShockwaveRing(self.parent.canvas, x, y, color_rgba)
            ), 0.10
        )

        # Floating score number
        if value and value > 0:
            self.floaters.append(
                FloatingNumber(self.parent, x, y + dp(10), value, color_rgba)
            )

        if not self._event:
            self._event = Clock.schedule_interval(self._update, 1/60)

    def _update(self, dt):
        alive_sparks   = []
        alive_rings    = []
        alive_floaters = []

        for p in self.sparks:
            if p.alive:
                p.update(dt)
                if p.alive:
                    alive_sparks.append(p)
                else:
                    p.remove()
            else:
                p.remove()

        for r in self.rings:
            if r.alive:
                r.update(dt)
                if r.alive:
                    alive_rings.append(r)
                else:
                    r.remove()
            else:
                r.remove()

        for f in self.floaters:
            if f.alive:
                f.update(dt)
                if f.alive:
                    alive_floaters.append(f)
                else:
                    f.remove()
            else:
                f.remove()

        self.sparks   = alive_sparks
        self.rings    = alive_rings
        self.floaters = alive_floaters

        if not self.sparks and not self.rings and not self.floaters:
            if self._event:
                self._event.cancel()
                self._event = None

    def clear(self):
        for p in self.sparks:   p.remove()
        for r in self.rings:    r.remove()
        for f in self.floaters: f.remove()
        self.sparks   = []
        self.rings    = []
        self.floaters = []
        if self._event:
            self._event.cancel()
            self._event = None


# ══════════════════════════════════════════════════════════════════════════
#  MERGE EFFECT HELPER
# ══════════════════════════════════════════════════════════════════════════

class MergeEffect:
    def __init__(self, particle_system: ParticleSystem):
        self.ps = particle_system

    def play(self, tile_cx, tile_cy, tile_color, value=None):
        r = min(tile_color[0] * 1.35, 1.0)
        g = min(tile_color[1] * 1.35, 1.0)
        b = min(tile_color[2] * 1.35, 1.0)
        self.ps.burst(tile_cx, tile_cy, (r, g, b, 1.0), value=value)