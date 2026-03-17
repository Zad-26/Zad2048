"""
Zad 2048 - Settings Screen
Preferences, volume sliders, statistics, and navigation buttons.
"""

import os
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp

from board_manager import StorageManager

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_IMG  = os.path.join(_ROOT, 'assets', 'images')
from animation_manager import AnimationManager, GradientAnimator


# ── Palette ────────────────────────────────────────────────────────────────
DARK_BG       = (0.07, 0.04, 0.14, 1)
DARK_CARD_BG  = (0.16, 0.11, 0.30, 1)
DARK_ACCENT   = (0.82, 0.35, 1.00, 1)
DARK_BTN      = [0.38, 0.10, 0.72, 1]
DARK_BTN_RED  = [0.65, 0.08, 0.12, 1]
DARK_TEXT     = (0.90, 0.88, 1.00, 1)
DARK_SUBTEXT  = (0.65, 0.58, 0.85, 1)
DARK_VAL      = (1.00, 1.00, 1.00, 1)

LIGHT_BG      = (0.96, 0.94, 0.99, 1)
LIGHT_CARD_BG = (0.88, 0.83, 0.97, 1)
LIGHT_ACCENT  = (0.50, 0.18, 0.82, 1)
LIGHT_BTN     = [0.55, 0.28, 0.90, 1]
LIGHT_BTN_RED = [0.75, 0.10, 0.15, 1]
LIGHT_TEXT    = (0.18, 0.10, 0.36, 1)
LIGHT_SUBTEXT = (0.42, 0.32, 0.65, 1)
LIGHT_VAL     = (0.12, 0.06, 0.30, 1)


# ── Helper widgets ────────────────────────────────────────────────────────

class Card(Widget):
    """Rounded card container."""
    def __init__(self, theme="dark", **kwargs):
        super().__init__(**kwargs)
        self.theme = theme
        bg = DARK_CARD_BG if theme == "dark" else LIGHT_CARD_BG
        with self.canvas:
            self._color_instr = Color(*bg)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
        self.bind(size=self._r, pos=self._r)

    def _r(self, *a):
        if self._bg:
            self._bg.pos  = self.pos
            self._bg.size = self.size

    def set_theme(self, theme):
        bg = DARK_CARD_BG if theme == "dark" else LIGHT_CARD_BG
        self._color_instr.rgba = bg


class ToggleRow(BoxLayout):
    """Label + Switch row."""
    def __init__(self, label_text, active=True, theme="dark", on_change=None, **kwargs):
        super().__init__(orientation="horizontal", spacing=dp(10),
                         padding=[dp(16), 0, dp(16), 0], **kwargs)
        tc = DARK_TEXT if theme == "dark" else LIGHT_TEXT
        lbl = Label(text=label_text, font_size="16sp", color=tc,
                    halign="left", valign="middle")
        lbl.bind(size=lbl.setter("text_size"))
        self.add_widget(lbl)
        self.switch = Switch(active=active, size_hint=(None, None), size=(dp(68), dp(38)))
        if on_change:
            self.switch.bind(active=lambda s, v: on_change(v))
        self.add_widget(self.switch)


class VolumeRow(BoxLayout):
    """
    Label + percentage label + Slider row for volume control.
    Supports enabled/disabled state — greys out when disabled.
    """
    def __init__(self, label_text, value=0.7, theme="dark", on_change=None, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(2),
                         padding=[dp(16), dp(4), dp(16), dp(4)], **kwargs)
        self.theme = theme
        self._on_change = on_change
        self._enabled = True

        tc  = DARK_TEXT    if theme == "dark" else LIGHT_TEXT
        ac  = DARK_ACCENT  if theme == "dark" else LIGHT_ACCENT

        # Top row: label + percentage
        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))

        self._lbl = Label(text=label_text, font_size="15sp", color=tc,
                    halign="left", valign="middle")
        self._lbl.bind(size=self._lbl.setter("text_size"))
        top.add_widget(self._lbl)

        self._pct_lbl = Label(
            text=f"{int(value * 100)}%",
            font_size="14sp", bold=True, color=ac,
            halign="right", valign="middle",
            size_hint_x=0.3,
        )
        self._pct_lbl.bind(size=self._pct_lbl.setter("text_size"))
        top.add_widget(self._pct_lbl)
        self.add_widget(top)

        # Slider
        self.slider = Slider(
            min=0.0, max=1.0, value=value, step=0.01,
            size_hint_y=None, height=dp(36),
        )
        self.slider.bind(value=self._on_slider)
        self.add_widget(self.slider)

    def _on_slider(self, slider, val):
        if not self._enabled:
            return
        self._pct_lbl.text = f"{int(val * 100)}%"
        if self._on_change:
            self._on_change(val)

    def get_value(self):
        return self.slider.value

    def set_value(self, v):
        self.slider.value = max(0.0, min(1.0, v))
        self._pct_lbl.text = f"{int(v * 100)}%"

    def set_enabled(self, enabled):
        """Grey out and disable interaction when toggled off."""
        self._enabled = enabled
        dim = 1.0 if enabled else 0.35
        self.opacity = dim
        self.slider.disabled = not enabled


class StatRow(BoxLayout):
    def __init__(self, label_text, value, theme="dark", **kwargs):
        super().__init__(orientation="horizontal", spacing=dp(10),
                         padding=[dp(16), 0, dp(16), 0], **kwargs)
        tc = DARK_SUBTEXT if theme == "dark" else LIGHT_SUBTEXT
        vc = DARK_VAL     if theme == "dark" else LIGHT_VAL
        lbl = Label(text=label_text, font_size="15sp", color=tc,
                    halign="left", valign="middle")
        lbl.bind(size=lbl.setter("text_size"))
        self.add_widget(lbl)
        self.val_lbl = Label(text=str(value), font_size="17sp", bold=True, color=vc,
                             halign="right", valign="middle", size_hint_x=0.35)
        self.val_lbl.bind(size=self.val_lbl.setter("text_size"))
        self.add_widget(self.val_lbl)


# ── Main Settings Screen ──────────────────────────────────────────────────

class SettingsScreen(FloatLayout):

    def __init__(self, on_back=None, on_theme_change=None, **kwargs):
        super().__init__(**kwargs)
        self.on_back_callback         = on_back
        self.on_theme_change_callback = on_theme_change
        self.storage = StorageManager()
        self.theme   = self.storage.get_setting("theme", "dark")
        self._bg_color_instr = None
        self._setup_ui()
        self._setup_gradient()

    def _setup_ui(self):
        with self.canvas.before:
            bg = DARK_BG if self.theme == "dark" else LIGHT_BG
            self._bg_color_instr = Color(*bg)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Wrap all content in a ScrollView so nothing gets cut off
        self._scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(4),
            scroll_type=['bars', 'content'],
        )
        # Inner container — height is set dynamically in _layout
        self._inner = FloatLayout(size_hint=(1, None), height=dp(900))
        self._scroll.add_widget(self._inner)
        self.add_widget(self._scroll)

        self._build_content()

    def _build_content(self):
        ac  = DARK_ACCENT   if self.theme == "dark" else LIGHT_ACCENT
        bb  = DARK_BTN      if self.theme == "dark" else LIGHT_BTN
        rb  = DARK_BTN_RED  if self.theme == "dark" else LIGHT_BTN_RED
        settings = self.storage.get_settings()

        # ── Title ──────────────────────────────────────────────────────────
        self.title_lbl = Label(
            text="Settings", font_size="30sp", bold=True, color=ac,
            halign="center", valign="middle",
            size_hint=(None, None), size=(dp(280), dp(48)),
        )
        self._inner.add_widget(self.title_lbl)

        # ══ PREFERENCES CARD ══════════════════════════════════════════════
        self.pref_card = Card(theme=self.theme, size_hint=(None, None))
        self._inner.add_widget(self.pref_card)

        self.pref_title = Label(
            text="Preferences", font_size="13sp", bold=True,
            color=ac, halign="left", valign="middle",
            size_hint=(None, None), size=(dp(260), dp(24)),
        )
        self._inner.add_widget(self.pref_title)

        self.theme_row = ToggleRow(
            label_text="Dark Mode",
            active=(settings["theme"] == "dark"),
            theme=self.theme, on_change=self._on_theme_toggle,
            size_hint=(None, None), size=(dp(300), dp(50)),
        )
        self.sound_row = ToggleRow(
            label_text="Sound Effects",
            active=settings.get("sound_enabled", True),
            theme=self.theme, on_change=self._on_sound_toggle,
            size_hint=(None, None), size=(dp(300), dp(50)),
        )
        self.bgm_row = ToggleRow(
            label_text="Background Music",
            active=settings.get("bgm_enabled", True),
            theme=self.theme, on_change=self._on_bgm_toggle,
            size_hint=(None, None), size=(dp(300), dp(50)),
        )
        self._inner.add_widget(self.theme_row)
        self._inner.add_widget(self.sound_row)
        self._inner.add_widget(self.bgm_row)

        # ══ VOLUME CARD ════════════════════════════════════════════════════
        self.vol_card = Card(theme=self.theme, size_hint=(None, None))
        self._inner.add_widget(self.vol_card)

        self.vol_title = Label(
            text="Volume", font_size="13sp", bold=True,
            color=ac, halign="left", valign="middle",
            size_hint=(None, None), size=(dp(260), dp(24)),
        )
        self._inner.add_widget(self.vol_title)

        sfx_vol = settings.get("sfx_volume", 0.70)
        bgm_vol = settings.get("bgm_volume", 0.30)

        self.sfx_vol_row = VolumeRow(
            label_text="Sound Effects Volume",
            value=sfx_vol, theme=self.theme,
            on_change=self._on_sfx_volume,
            size_hint=(None, None), size=(dp(300), dp(64)),
        )
        self.bgm_vol_row = VolumeRow(
            label_text="Music Volume",
            value=bgm_vol, theme=self.theme,
            on_change=self._on_bgm_volume,
            size_hint=(None, None), size=(dp(300), dp(64)),
        )
        self._inner.add_widget(self.sfx_vol_row)
        self._inner.add_widget(self.bgm_vol_row)

        # Apply initial enabled state based on current toggle settings
        self.sfx_vol_row.set_enabled(settings.get("sound_enabled", True))
        self.bgm_vol_row.set_enabled(settings.get("bgm_enabled", True))

        # ══ STATISTICS CARD ════════════════════════════════════════════════
        stats = self.storage.get_stats()
        self.stats_card = Card(theme=self.theme, size_hint=(None, None))
        self._inner.add_widget(self.stats_card)

        self.stats_title = Label(
            text="Statistics", font_size="13sp", bold=True,
            color=ac, halign="left", valign="middle",
            size_hint=(None, None), size=(dp(260), dp(24)),
        )
        self._inner.add_widget(self.stats_title)

        stat_data = [
            ("Best Score",   stats.get("best_score", 0)),
            ("Highest Tile", stats.get("highest_tile", 0)),
            ("Total Games",  stats.get("total_games", 0)),
            ("Total Moves",  stats.get("total_moves", 0)),
        ]
        self.stat_rows = []
        for label, value in stat_data:
            row = StatRow(label_text=label, value=value, theme=self.theme,
                          size_hint=(None, None), size=(dp(300), dp(40)))
            self.stat_rows.append(row)
            self._inner.add_widget(row)

        # ══ BUTTONS ════════════════════════════════════════════════════════
        self.reset_btn = Button(
            text="Reset Statistics", font_size="14sp",
            background_normal="", background_color=rb, color=(1,1,1,1),
            size_hint=(None, None), size=(dp(180), dp(42)),
        )
        self.reset_btn.bind(on_press=self._on_reset_stats)
        self._inner.add_widget(self.reset_btn)

        # Back icon button — small, top-left corner, added to OUTER layout not inner
        back_icon = os.path.join(_IMG, "back_icon.png")
        self.back_btn = Button(
            background_normal=back_icon,
            background_down=back_icon,
            background_color=(1, 1, 1, 1),
            border=(0, 0, 0, 0),
            size_hint=(None, None), size=(dp(44), dp(44)),
        )
        self.back_btn.bind(on_press=self._on_back)
        self.add_widget(self.back_btn)   # added to self, not _inner



        self.bind(size=self._layout, pos=self._layout)

    # ── Layout ────────────────────────────────────────────────────────────

    def _layout(self, *args):
        w, h = self.size
        px, py = self.pos
        cx = px + w / 2
        card_w = min(w - dp(28), dp(340))

        # Pin back icon button to top-left corner of outer screen
        self.back_btn.pos = (px + dp(10), py + h - dp(54))

        # All items stacked — compute total content height
        title_h      = dp(60)
        pref_card_h  = dp(50) * 3 + dp(34)
        vol_card_h   = dp(64) * 2 + dp(34)
        stats_card_h = dp(40) * 4 + dp(36)
        reset_h      = dp(52)
        back_h       = dp(56)
        about_h      = dp(56)
        gap          = dp(12)
        bottom_pad   = dp(20)

        total_content_h = (dp(16) + title_h + gap + pref_card_h + gap +
                           vol_card_h + gap + stats_card_h + gap +
                           dp(44) + bottom_pad)

        # Make inner tall enough to scroll, at least screen height
        inner_h = max(total_content_h, h)
        self._inner.height = inner_h
        self._inner.width  = w
        self._scroll.size  = (w, h)
        self._scroll.pos   = (px, py)

        # Layout relative to inner widget (inner always starts at 0,0 in scroll)
        # Start from top of inner
        iw = w   # inner width
        icx = iw / 2  # inner center x (relative)

        y = inner_h - dp(16)

        # Title
        y -= title_h
        self.title_lbl.center_x = icx
        self.title_lbl.top = y + title_h
        self.title_lbl.text_size = self.title_lbl.size

        y -= gap

        # Preferences card
        y -= pref_card_h
        self.pref_card.size = (card_w, pref_card_h)
        self.pref_card.pos  = (icx - card_w / 2, y)
        self.pref_title.pos = (icx - card_w / 2 + dp(14), y + pref_card_h - dp(26))
        self.pref_title.text_size = self.pref_title.size
        for i, row in enumerate([self.theme_row, self.sound_row, self.bgm_row]):
            row.size = (card_w, dp(50))
            row.pos  = (icx - card_w / 2,
                        y + pref_card_h - dp(34) - (i + 1) * dp(50))

        y -= gap

        # Volume card
        y -= vol_card_h
        self.vol_card.size = (card_w, vol_card_h)
        self.vol_card.pos  = (icx - card_w / 2, y)
        self.vol_title.pos = (icx - card_w / 2 + dp(14), y + vol_card_h - dp(26))
        self.vol_title.text_size = self.vol_title.size
        self.bgm_vol_row.size = (card_w, dp(64))
        self.bgm_vol_row.pos  = (icx - card_w / 2, y + dp(14) + dp(64))
        self.sfx_vol_row.size = (card_w, dp(64))
        self.sfx_vol_row.pos  = (icx - card_w / 2, y + dp(14))

        y -= gap

        # Stats card
        y -= stats_card_h
        self.stats_card.size = (card_w, stats_card_h)
        self.stats_card.pos  = (icx - card_w / 2, y)
        self.stats_title.pos = (icx - card_w / 2 + dp(14), y + stats_card_h - dp(26))
        self.stats_title.text_size = self.stats_title.size
        for i, row in enumerate(self.stat_rows):
            row.size = (card_w, dp(40))
            row.pos  = (icx - card_w / 2,
                        y + stats_card_h - dp(34) - (i + 1) * dp(40))

        y -= gap

        # Reset button
        self.reset_btn.size = (dp(200), dp(44))
        self.reset_btn.center_x = icx
        self.reset_btn.top = y
        # (back_btn is pinned to top-left of outer screen, not inner scroll)
        gap_tmp = gap  # keep gap for spacing below

        # About button


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

    # ── Callbacks ─────────────────────────────────────────────────────────

    def _on_theme_toggle(self, value):
        new_theme = "dark" if value else "light"
        self.storage.set_setting("theme", new_theme)
        self._apply_theme(new_theme)
        if self.on_theme_change_callback:
            self.on_theme_change_callback(new_theme)

    def _apply_theme(self, theme):
        """Instantly update all colours on the settings screen to the new theme."""
        self.theme = theme

        # ── Background ────────────────────────────────────────────────────
        bg = DARK_BG if theme == "dark" else LIGHT_BG
        Animation(r=bg[0], g=bg[1], b=bg[2], duration=0.35, t="out_quad").start(self._bg_color_instr)

        # ── Gradient animator ─────────────────────────────────────────────
        self.grad_animator.set_theme(theme)

        # ── Accent / button colours ───────────────────────────────────────
        ac  = DARK_ACCENT   if theme == "dark" else LIGHT_ACCENT
        bb  = DARK_BTN      if theme == "dark" else LIGHT_BTN
        rb  = DARK_BTN_RED  if theme == "dark" else LIGHT_BTN_RED
        card_bg = DARK_CARD_BG if theme == "dark" else LIGHT_CARD_BG
        tc  = DARK_TEXT     if theme == "dark" else LIGHT_TEXT

        # Title
        self.title_lbl.color = ac

        # Preference card section title
        self.pref_title.color  = ac
        self.vol_title.color   = ac
        self.stats_title.color = ac

        # Cards background — use the stored Color instruction
        for card in (self.pref_card, self.vol_card, self.stats_card):
            card.set_theme(theme)

        # Buttons
        self.reset_btn.background_color = rb
        self.back_btn.background_color  = (1, 1, 1, 1)

        # Toggle row labels
        for row in (self.theme_row, self.sound_row, self.bgm_row):
            for child in row.children:
                if hasattr(child, "color") and not hasattr(child, "switch"):
                    child.color = tc

        # Stat rows
        for row in self.stat_rows:
            vc = DARK_VAL  if theme == "dark" else LIGHT_VAL
            sc = DARK_SUBTEXT if theme == "dark" else LIGHT_SUBTEXT
            row.val_lbl.color = vc
            for child in row.children:
                if child is not row.val_lbl and hasattr(child, "color"):
                    child.color = sc

        # Volume rows
        for vol_row in (self.sfx_vol_row, self.bgm_vol_row):
            vc = DARK_ACCENT if theme == "dark" else LIGHT_ACCENT
            tc2 = DARK_TEXT if theme == "dark" else LIGHT_TEXT
            vol_row._pct_lbl.color = vc
            vol_row._lbl.color = tc2

    def _on_sound_toggle(self, value):
        self.storage.set_setting("sound_enabled", value)
        self.sfx_vol_row.set_enabled(value)
        try:
            from game_screen import get_sound_manager
            get_sound_manager().set_sfx_enabled(value)
        except Exception:
            pass

    def _on_bgm_toggle(self, value):
        self.storage.set_setting("bgm_enabled", value)
        self.bgm_vol_row.set_enabled(value)
        try:
            from game_screen import get_sound_manager
            get_sound_manager().set_bgm_enabled(value)
        except Exception:
            pass

    def _on_sfx_volume(self, value):
        """Live-update SFX volume and persist."""
        self.storage.set_setting("sfx_volume", round(value, 2))
        try:
            from game_screen import get_sound_manager
            sm = get_sound_manager()
            for snd in sm._sfx.values():
                snd.set_volume(value)
        except Exception:
            pass

    def _on_bgm_volume(self, value):
        """Live-update BGM volume and persist."""
        self.storage.set_setting("bgm_volume", round(value, 2))
        try:
            from game_screen import get_sound_manager
            get_sound_manager().set_bgm_volume(value)
        except Exception:
            pass

    def _on_reset_stats(self, btn):
        AnimationManager.button_press(btn)
        self.storage.reset_stats()
        for row in self.stat_rows:
            row.val_lbl.text = "0"

    def _on_back(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(
            lambda dt: self.on_back_callback() if self.on_back_callback else None, 0.15)

    def refresh_stats(self):
        """Re-read stats from storage and update all stat row labels."""
        stats = self.storage.get_stats()
        fresh = [
            stats.get("best_score",   0),
            stats.get("highest_tile", 0),
            stats.get("total_games",  0),
            stats.get("total_moves",  0),
        ]
        for row, val in zip(self.stat_rows, fresh):
            row.val_lbl.text = str(val)

    def on_leave(self):
        self.grad_animator.stop()