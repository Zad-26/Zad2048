"""
Zad 2048 - Menu Screen
Shown after launch. Has Play, About, and Quit buttons.
Background image adapts to light/dark theme.
"""
import os, sys

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.app import App

from board_manager import StorageManager
from animation_manager import AnimationManager

_HERE        = os.path.dirname(os.path.abspath(__file__))
_ROOT        = os.path.dirname(_HERE)
_IMG         = os.path.join(_ROOT, "assets", "images")
_BG_PATH     = os.path.join(_IMG, "menu_bg.png")


class MenuScreen(FloatLayout):

    def __init__(self, on_play=None, on_about=None, on_quit=None, **kwargs):
        super().__init__(**kwargs)
        self.on_play_callback  = on_play
        self.on_about_callback = on_about
        self.on_quit_callback  = on_quit
        self.storage = StorageManager()
        self.theme   = self.storage.get_setting("theme", "dark")
        self._bg_rect = None
        self._setup_ui()
        Clock.schedule_once(self._animate_in, 0.1)

    def _setup_ui(self):
        bg_path = _BG_PATH
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._bg_rect = Rectangle(source=bg_path, pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)
        self._build()

    def _build(self):
        # Accent and text colours chosen to stand out on both bg variants
        ac   = (0.42, 0.08, 0.75, 1)   # deep purple — readable on light bg
        sc   = (0.35, 0.22, 0.62, 1)   # muted purple tagline

        # ── Logo ──────────────────────────────────────────────────────────
        self.logo = KivyImage(
            source=os.path.join(_IMG, "icon.png"),
            fit_mode="contain",
            size_hint=(None, None), size=(dp(110), dp(110)),
            opacity=0,
        )
        self.add_widget(self.logo)

        # ── Title ──────────────────────────────────────────────────────────
        self.title_lbl = Label(
            text="Zad 2048",
            font_size="38sp", bold=True, color=ac,
            halign="center", valign="middle",
            size_hint=(None, None), size=(dp(300), dp(54)),
            opacity=0,
        )
        self.add_widget(self.title_lbl)

        # ── Tagline ────────────────────────────────────────────────────────
        self.tag_lbl = Label(
            text="The Ultimate Puzzle",
            font_size="16sp", color=sc,
            halign="center", valign="middle",
            size_hint=(None, None), size=(dp(280), dp(30)),
            opacity=0,
        )
        self.add_widget(self.tag_lbl)

        # ── Buttons ────────────────────────────────────────────────────────
        self.play_btn = Button(
            text="Play",
            font_size="22sp", bold=True,
            background_normal="", background_color=[0.45, 0.10, 0.82, 1],
            size_hint=(None, None), size=(dp(220), dp(58)),
            color=(1, 1, 1, 1), opacity=0,
        )
        self.about_btn = Button(
            text="About",
            font_size="18sp", bold=True,
            background_normal="", background_color=[0.20, 0.12, 0.48, 0.95],
            size_hint=(None, None), size=(dp(220), dp(50)),
            color=(1, 1, 1, 1), opacity=0,
        )
        self.quit_btn = Button(
            text="Quit",
            font_size="18sp", bold=True,
            background_normal="", background_color=[0.65, 0.08, 0.12, 0.95],
            size_hint=(None, None), size=(dp(220), dp(50)),
            color=(1, 1, 1, 1), opacity=0,
        )

        self.play_btn.bind(on_press=self._on_play)
        self.about_btn.bind(on_press=self._on_about)
        self.quit_btn.bind(on_press=self._on_quit)

        for w in (self.play_btn, self.about_btn, self.quit_btn):
            self.add_widget(w)

        self.bind(size=self._layout, pos=self._layout)

    def _layout(self, *args):
        w, h = self.size
        px, py = self.pos
        cx = px + w / 2

        btn_gap   = dp(14)
        btn_h1    = dp(58)
        btn_h2    = dp(50)
        total_btn = btn_h1 + btn_h2 * 2 + btn_gap * 2

        # Buttons sit in the bottom 38% of the screen
        btn_top_y  = py + h * 0.38
        play_y     = btn_top_y - btn_h1
        about_y    = play_y - btn_h2 - btn_gap
        quit_y     = about_y - btn_h2 - btn_gap

        self.play_btn.size     = (dp(220), btn_h1)
        self.play_btn.center_x = cx
        self.play_btn.y        = play_y

        self.about_btn.size     = (dp(220), btn_h2)
        self.about_btn.center_x = cx
        self.about_btn.y        = about_y

        self.quit_btn.size     = (dp(220), btn_h2)
        self.quit_btn.center_x = cx
        self.quit_btn.y        = quit_y

        # Logo — top area, 8% padding from top
        logo_h = dp(110)
        self.logo.size     = (logo_h, logo_h)
        self.logo.center_x = cx
        self.logo.y        = py + h * 0.92 - logo_h

        # Space between bottom of logo and top of Play button
        space_between = play_y - (self.logo.y + logo_h)

        # Place title + tagline in the CENTER of that space
        title_h = dp(54)
        tag_h   = dp(30)
        block_h = title_h + dp(8) + tag_h
        block_y = self.logo.y + logo_h + (space_between - block_h) / 2

        self.title_lbl.size     = (dp(300), title_h)
        self.title_lbl.center_x = cx
        self.title_lbl.y        = block_y + tag_h + dp(8)
        self.title_lbl.text_size = self.title_lbl.size

        self.tag_lbl.size     = (dp(280), tag_h)
        self.tag_lbl.center_x = cx
        self.tag_lbl.y        = block_y
        self.tag_lbl.text_size = self.tag_lbl.size

    def _update_bg(self, *args):
        self._bg_rect.pos  = self.pos
        self._bg_rect.size = self.size

    def _animate_in(self, dt):
        self._layout()
        pairs = [
            (self.logo,      0.00),
            (self.title_lbl, 0.15),
            (self.tag_lbl,   0.25),
            (self.play_btn,  0.38),
            (self.about_btn, 0.48),
            (self.quit_btn,  0.56),
        ]
        for widget, delay in pairs:
            orig_y = widget.y
            widget.y -= dp(18)
            Clock.schedule_once(
                lambda dt, w=widget, oy=orig_y: (
                    Animation(opacity=1, y=oy, duration=0.40, t="out_cubic").start(w)
                ), delay,
            )

    def _on_play(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(
            lambda dt: self.on_play_callback() if self.on_play_callback else None, 0.18)

    def _on_about(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(
            lambda dt: self.on_about_callback() if self.on_about_callback else None, 0.15)

    def _on_quit(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(lambda dt: App.get_running_app().stop(), 0.25)

    def on_leave(self):
        pass