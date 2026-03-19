"""
Zad 2048 - Main Application Entry Point
Screen flow: Splash → Menu → Game
                          ↓       ↓
                        About  Settings → About
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ui"))

from kivy.config import Config
Config.set("kivy", "exit_on_escape", "0")

import os as _os
_is_android = "ANDROID_ARGUMENT" in _os.environ

if not _is_android:
    Config.set("graphics", "resizable", "1")
    Config.set("input", "mouse", "mouse,multitouch_on_demand")

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window

if not _is_android:
    Window.size = (400, 720)

from menu_screen     import MenuScreen
from game_screen     import GameScreen
from settings_screen import SettingsScreen
from about_screen    import AboutScreen
from game_over_screen import GameOverScreen, VictoryScreen
from board_manager   import StorageManager


class RootLayout(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage      = StorageManager()
        self._current     = None
        self._overlay     = None
        self._game_screen = None
        # Track where About was opened from so we can return correctly
        self._about_origin = "menu"
        Clock.schedule_once(self._show_splash, 0)

    # ── Generic screen helpers ─────────────────────────────────────────────

    def _clear(self):
        if self._current and self._current.parent:
            self.remove_widget(self._current)
        self._current = None

    def _show(self, screen):
        screen.size = self.size
        screen.pos  = self.pos
        self.bind(size=screen.setter("size"), pos=screen.setter("pos"))
        self._current = screen
        self.add_widget(screen)

    # ── Splash ─────────────────────────────────────────────────────────────

    def _show_splash(self, dt):
        # Start BGM immediately then show menu
        Clock.schedule_once(self._start_bgm, 0.1)
        self._show_menu()

    def _start_bgm(self, dt):
        try:
            from game_screen import get_sound_manager
            sm = get_sound_manager()
            sm.set_sfx_enabled(self.storage.get_setting("sound_enabled", True))
            bgm_on  = self.storage.get_setting("bgm_enabled", True)
            sfx_vol = self.storage.get_setting("sfx_volume", 0.70)
            bgm_vol = self.storage.get_setting("bgm_volume", 0.30)
            sm.bgm_enabled = bgm_on
            for snd in sm._sfx.values():
                try: snd.set_volume(sfx_vol)
                except Exception: pass
            sm.set_bgm_volume(bgm_vol)
            if bgm_on:
                sm.start_bgm()
        except Exception as e:
            print(f"[Main] BGM error: {e}")

    # ── Menu ───────────────────────────────────────────────────────────────

    def _show_menu(self):
        self._show(MenuScreen(
            on_play=self._on_play,
            on_about=self._on_menu_about,
            on_quit=None,   # handled inside MenuScreen via App.stop()
        ))

    def _on_play(self):
        self._clear()
        self._show_game()

    def _on_menu_about(self):
        self._about_origin = "menu"
        self._clear()
        self._show_about()

    # ── Game ───────────────────────────────────────────────────────────────

    def _show_game(self):
        is_new = self._game_screen is None
        if is_new:
            self._game_screen = GameScreen(
                on_settings=self._show_settings,
                on_game_over=self._show_game_over,
                on_win=self._show_victory,
                on_home=self._on_game_home,
            )
        self._show(self._game_screen)
        if hasattr(self._game_screen, "refresh_theme"):
            self._game_screen.refresh_theme()
        if not is_new:
            self._game_screen.on_enter()

    def _on_game_home(self):
        """Home button in game → go back to menu."""
        self._clear()
        self._game_screen = None  # reset game on returning to menu
        self._show_menu()

    # ── Settings ───────────────────────────────────────────────────────────

    def _show_settings(self):
        self._clear()
        s = SettingsScreen(
            on_back=self._on_settings_back,
            on_theme_change=self._on_theme_change,
        )
        self._show(s)
        # Always refresh stats so they reflect latest game data
        if hasattr(s, "refresh_stats"):
            s.refresh_stats()

    def _on_settings_back(self):
        self._clear()
        self._show_game()

    def _on_theme_change(self, new_theme):
        if self._game_screen:
            self._game_screen.theme = new_theme

    # ── About ──────────────────────────────────────────────────────────────

    def _show_about(self):
        self._show(AboutScreen(on_back=self._on_about_back))

    def _on_about_back(self):
        self._clear()
        if self._about_origin == "settings":
            self._show_settings()
        else:
            self._show_menu()

    # ── Game Over / Victory overlays ───────────────────────────────────────

    def _show_game_over(self, score):
        theme = self.storage.get_setting("theme", "dark")
        best  = self.storage.get_best_score()
        ov = GameOverScreen(
            score=score, best_score=best, theme=theme,
            on_restart=self._on_game_over_restart,
            on_menu=self._on_game_over_menu,
        )
        ov.size = self.size
        ov.pos  = self.pos
        self.bind(size=ov.setter("size"), pos=ov.setter("pos"))
        self._overlay = ov
        self.add_widget(ov)

    def _show_victory(self, score):
        theme = self.storage.get_setting("theme", "dark")
        ov = VictoryScreen(
            score=score, theme=theme,
            on_continue=self._on_victory_continue,
            on_restart=self._on_victory_restart,
        )
        ov.size = self.size
        ov.pos  = self.pos
        self.bind(size=ov.setter("size"), pos=ov.setter("pos"))
        self._overlay = ov
        self.add_widget(ov)

    def _remove_overlay(self):
        if self._overlay and self._overlay.parent:
            self.remove_widget(self._overlay)
        self._overlay = None

    def _on_game_over_restart(self):
        self._remove_overlay()
        if self._game_screen:
            self._game_screen._start_new_game()

    def _on_game_over_menu(self):
        self._remove_overlay()
        self._game_screen = None
        self._clear()
        self._show_menu()

    def _on_victory_continue(self):
        self._remove_overlay()

    def _on_victory_restart(self):
        self._remove_overlay()
        if self._game_screen:
            self._game_screen._start_new_game()


class Zad2048App(App):
    title = "Zad 2048"

    def build(self):
        import os as _os
        _icon = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                              "assets", "images", "icon.png")
        if _os.path.exists(_icon):
            self.icon = _icon
        return RootLayout()

    def _save_game_if_active(self):
        """Save game state if a game is currently in progress."""
        try:
            root = self.root
            if root and root._game_screen:
                gs = root._game_screen
                if gs.logic and gs.logic.score >= 0:
                    gs._save_game_state()
                    print("[App] Game state saved on pause/stop")
        except Exception as e:
            print(f"[App] Could not save game state: {e}")

    def on_pause(self):
        # Called when app is backgrounded on Android
        self._save_game_if_active()
        return True  # Must return True to allow resume

    def on_stop(self):
        # Called when app is fully closed (swiped away from recents)
        self._save_game_if_active()

    def on_resume(self):
        pass


if __name__ == "__main__":
    Zad2048App().run()
