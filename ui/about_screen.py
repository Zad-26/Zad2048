"""
Zad 2048 - About Screen
Developer profile for Zad Amparo.
Photo is pre-cropped to a circle (zad_photo.png) so no stencil needed.
"""

import os
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp

from board_manager import StorageManager
from animation_manager import AnimationManager, GradientAnimator

_HERE        = os.path.dirname(os.path.abspath(__file__))
_ROOT        = os.path.dirname(_HERE)
# Use the pre-cropped circular photo
_PHOTO_PATH  = os.path.join(_ROOT, "assets", "images", "zad_photo.png")


# ── Spinning ring avatar container ────────────────────────────────────────

class AvatarRing(Widget):
    """
    Draws animated spinning accent rings around the photo.
    The photo itself is a KivyImage child (pre-cropped circle PNG).
    """

    def __init__(self, photo_path, theme="dark", **kwargs):
        super().__init__(**kwargs)
        self.photo_path  = photo_path
        self.theme       = theme
        self._angle      = 0
        self._img        = None
        self._ring_instrs = []

        # Add the pre-cropped circular photo as a child Image widget
        if os.path.exists(photo_path):
            self._img = KivyImage(
                source=photo_path,
                fit_mode="contain",
                size_hint=(None, None),
            )
            self.add_widget(self._img)
        else:
            print(f"[About] Photo not found: {photo_path}")

        self.bind(size=self._redraw, pos=self._redraw)
        Clock.schedule_interval(self._spin, 1 / 30)

    def _spin(self, dt):
        self._angle = (self._angle + 1.5) % 360
        self._draw_rings()

    def _redraw(self, *args):
        cx = self.x + self.width  / 2
        cy = self.y + self.height / 2
        r  = min(self.width, self.height) / 2

        # Position the photo widget centered, slightly inset from ring
        img_r = r - dp(8)
        if self._img:
            self._img.size = (img_r * 2, img_r * 2)
            self._img.pos  = (cx - img_r, cy - img_r)

        # Static background glow
        self.canvas.before.clear()
        with self.canvas.before:
            # Outer soft glow
            for i in range(6):
                gr = r + dp(4) + i * dp(5)
                Color(0.72, 0.20, 1.00, 0.07 - i * 0.01)
                Ellipse(pos=(cx - gr, cy - gr), size=(gr*2, gr*2))

            # Fallback solid circle if no photo loaded
            if not self._img:
                Color(0.28, 0.10, 0.52, 1)
                Ellipse(pos=(cx - r + dp(8), cy - r + dp(8)),
                        size=((r - dp(8))*2, (r - dp(8))*2))

        self._draw_rings()

    def _draw_rings(self):
        # Remove old ring canvas instructions
        for instr in self._ring_instrs:
            try:
                self.canvas.remove(instr)
            except Exception:
                pass
        self._ring_instrs = []

        cx = self.x + self.width  / 2
        cy = self.y + self.height / 2
        r  = min(self.width, self.height) / 2
        rr = r + dp(2)

        with self.canvas:
            # Primary arc — violet
            c1 = Color(0.82, 0.35, 1.00, 0.95)
            l1 = Line(circle=(cx, cy, rr,
                               self._angle,
                               self._angle + 210), width=dp(3.5))
            # Secondary arc — cyan
            c2 = Color(0.30, 0.85, 1.00, 0.75)
            l2 = Line(circle=(cx, cy, rr,
                               self._angle + 210,
                               self._angle + 350), width=dp(2))
            # Thin outer ring
            c3 = Color(1.00, 1.00, 1.00, 0.20)
            l3 = Line(circle=(cx, cy, rr + dp(5)), width=dp(1))
            self._ring_instrs = [c1, l1, c2, l2, c3, l3]


# ── Info row ──────────────────────────────────────────────────────────────

class InfoRow(Widget):
    def __init__(self, label, value, theme="dark", **kwargs):
        super().__init__(**kwargs)
        ac = (0.82, 0.35, 1.00, 1) if theme == "dark" else (0.55, 0.18, 0.85, 1)
        tc = (0.90, 0.88, 1.00, 1) if theme == "dark" else (0.18, 0.10, 0.36, 1)

        self._lbl = Label(text=label, font_size="14sp", bold=True, color=ac,
                          halign="right", valign="middle", size_hint=(None, None))
        self._val = Label(text=value, font_size="15sp", color=tc,
                          halign="left", valign="middle", size_hint=(None, None))
        self._lbl.bind(size=self._lbl.setter("text_size"))
        self._val.bind(size=self._val.setter("text_size"))
        self.add_widget(self._lbl)
        self.add_widget(self._val)
        self.bind(size=self._rel, pos=self._rel)

    def _rel(self, *args):
        col_w = dp(90)
        self._lbl.size      = (col_w, self.height)
        self._lbl.pos       = (self.x, self.y)
        self._lbl.text_size = (col_w, self.height)
        self._val.size      = (self.width - col_w - dp(12), self.height)
        self._val.pos       = (self.x + col_w + dp(12), self.y)
        self._val.text_size = (self.width - col_w - dp(12), self.height)


# ── About Screen ──────────────────────────────────────────────────────────

class AboutScreen(FloatLayout):

    def __init__(self, on_back=None, **kwargs):
        super().__init__(**kwargs)
        self.on_back_callback = on_back
        self.storage = StorageManager()
        self.theme   = self.storage.get_setting("theme", "dark")
        self._bg_color_instr = None
        self._setup_ui()
        self._setup_gradient()
        Clock.schedule_once(self._animate_in, 0.05)

    def _setup_ui(self):
        start_bg = (0.07, 0.04, 0.14, 1) if self.theme == "dark" else (0.92, 0.88, 0.98, 1)
        with self.canvas.before:
            self._bg_color_instr = Color(*start_bg)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)
        self._build_content()

    def _build_content(self):
        ac      = (0.82, 0.35, 1.00, 1) if self.theme == "dark" else (0.55, 0.18, 0.85, 1)
        sc      = (0.65, 0.58, 0.88, 1) if self.theme == "dark" else (0.42, 0.32, 0.65, 1)
        bb      = [0.38, 0.10, 0.72, 1] if self.theme == "dark" else [0.55, 0.28, 0.90, 1]
        card_bg = (0.16, 0.11, 0.30, 1) if self.theme == "dark" else (0.86, 0.80, 0.96, 1)

        # Title
        self.page_title = Label(
            text="About", font_size="28sp", bold=True, color=ac,
            halign="center", valign="middle",
            size_hint=(None, None), size=(dp(200), dp(44)), opacity=0,
        )
        self.add_widget(self.page_title)

        # Circular photo with spinning ring
        self.avatar = AvatarRing(
            photo_path=_PHOTO_PATH,
            theme=self.theme,
            size_hint=(None, None), size=(dp(130), dp(130)), opacity=0,
        )
        self.add_widget(self.avatar)

        # Name
        self.name_lbl = Label(
            text="Zad Amparo", font_size="30sp", bold=True, color=ac,
            halign="center", valign="middle",
            size_hint=(None, None), size=(dp(300), dp(44)), opacity=0,
        )
        self.add_widget(self.name_lbl)

        # Role
        self.role_lbl = Label(
            text="Developer  &  Designer",
            font_size="14sp", color=sc, halign="center", valign="middle",
            size_hint=(None, None), size=(dp(300), dp(26)), opacity=0,
        )
        self.add_widget(self.role_lbl)

        # Info card
        self.info_card = Widget(size_hint=(None, None), opacity=0)
        with self.info_card.canvas:
            Color(*card_bg)
            self._info_bg = RoundedRectangle(
                pos=self.info_card.pos, size=self.info_card.size, radius=[dp(16)])
        self.info_card.bind(
            size=lambda w, v: setattr(self._info_bg, "size", v),
            pos =lambda w, v: setattr(self._info_bg, "pos",  v),
        )
        self.add_widget(self.info_card)

        info_data = [
            ("Game",     "Zad 2048"),
            ("Tech",     "Python & Kivy"),
            ("Version",  "1.0.0"),
            ("Platform", "Android"),
        ]
        self.info_rows = []
        for lbl, val in info_data:
            row = InfoRow(label=lbl, value=val, theme=self.theme,
                          size_hint=(None, None), size=(dp(300), dp(36)))
            self.info_rows.append(row)
            self.add_widget(row)

        # Quote
        self.quote_lbl = Label(
            text='"Crafted with passion to bring\na modern, beautiful twist\nto the classic 2048 puzzle."',
            font_size="13sp", color=sc, halign="center", valign="middle",
            size_hint=(None, None), size=(dp(300), dp(62)), opacity=0,
        )
        self.quote_lbl.bind(size=self.quote_lbl.setter("text_size"))
        self.add_widget(self.quote_lbl)

        # Home icon button — top-left corner
        home_icon = os.path.join(_ROOT, "assets", "images", "home_icon.png")
        self.back_btn = Button(
            background_normal=home_icon,
            background_down=home_icon,
            background_color=(1, 1, 1, 1),
            border=(0, 0, 0, 0),
            size_hint=(None, None), size=(dp(48), dp(48)),
            opacity=1,
        )
        self.back_btn.bind(on_press=self._on_back)
        self.add_widget(self.back_btn)

        self.bind(size=self._layout, pos=self._layout)

    def _layout(self, *args):
        w, h = self.size
        px, py = self.pos
        cx = px + w / 2
        card_w = min(w - dp(28), dp(360))

        # Distribute vertical space evenly across all content
        top_pad    = dp(70)    # space for title + gap
        avatar_h   = dp(150)   # bigger avatar
        name_h     = dp(52)
        role_h     = dp(32)
        info_h     = len(self.info_rows) * dp(44) + dp(24)
        quote_h    = dp(72)
        gap        = (h - top_pad - avatar_h - name_h - role_h - info_h - quote_h - dp(30)) / 5
        gap        = max(dp(8), min(gap, dp(22)))  # clamp gap

        y = py + h - dp(16)

        # Title
        self.page_title.size      = (dp(300), dp(50))
        self.page_title.font_size = "32sp"
        self.page_title.center_x  = cx
        self.page_title.top       = y
        self.page_title.text_size = self.page_title.size
        y -= dp(50) + gap

        # Avatar — bigger
        self.avatar.size     = (avatar_h, avatar_h)
        self.avatar.center_x = cx
        self.avatar.y        = y - avatar_h
        y -= avatar_h + gap

        # Name — bigger font
        self.name_lbl.size      = (card_w, name_h)
        self.name_lbl.font_size = "34sp"
        self.name_lbl.center_x  = cx
        self.name_lbl.top       = y
        self.name_lbl.text_size = (card_w, name_h)
        y -= name_h + dp(4)

        # Role
        self.role_lbl.size      = (card_w, role_h)
        self.role_lbl.font_size = "16sp"
        self.role_lbl.center_x  = cx
        self.role_lbl.top       = y
        self.role_lbl.text_size = (card_w, role_h)
        y -= role_h + gap

        # Info card — bigger rows
        self.info_card.size = (card_w, info_h)
        self.info_card.pos  = (cx - card_w / 2, y - info_h)
        for i, row in enumerate(self.info_rows):
            row.size = (card_w - dp(24), dp(42))
            row.pos  = (cx - card_w / 2 + dp(12),
                        y - info_h + dp(10) + (len(self.info_rows)-1-i) * dp(44))
        y -= info_h + gap

        # Quote — bigger
        self.quote_lbl.size      = (card_w, quote_h)
        self.quote_lbl.font_size = "15sp"
        self.quote_lbl.center_x  = cx
        self.quote_lbl.top       = y
        self.quote_lbl.text_size = (card_w, quote_h)

        # Home button — pinned to top-left of screen
        self.back_btn.pos = (px + dp(10), py + h - dp(58))

    def _update_bg(self, *args):
        self._bg_rect.pos  = self.pos
        self._bg_rect.size = self.size

    def _update_bg_color(self, r, g, b):
        if self._bg_color_instr:
            self._bg_color_instr.rgb = (r, g, b)

    def _setup_gradient(self):
        self.grad_animator = GradientAnimator(
            callback=self._update_bg_color, theme=self.theme)
        self.grad_animator.start()

    def _animate_in(self, dt):
        pairs = [
            (self.page_title, 0.00),
            (self.avatar,     0.12),
            (self.name_lbl,   0.22),
            (self.role_lbl,   0.30),
            (self.info_card,  0.38),
            (self.quote_lbl,  0.52),

        ]
        for row in self.info_rows:
            pairs.append((row, 0.38))
        for widget, delay in pairs:
            Clock.schedule_once(
                lambda dt, w=widget: Animation(opacity=1, duration=0.4, t="out_quad").start(w),
                delay,
            )

    def _on_back(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(
            lambda dt: self.on_back_callback() if self.on_back_callback else None, 0.15)

    def on_leave(self):
        self.grad_animator.stop()