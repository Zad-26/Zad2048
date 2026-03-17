"""
Zad 2048 - Game Over and Victory Screens
Displayed when the game ends (loss) or when the player reaches 2048 (win).
"""

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp

from board_manager import StorageManager
from animation_manager import AnimationManager, GradientAnimator


class OverlayCard(Widget):
    """A large centered card shown on game over / win screens."""

    def __init__(self, theme="dark", win=False, **kwargs):
        super().__init__(**kwargs)
        self.theme = theme
        self.win = win

        with self.canvas:
            if win:
                # Gold/purple gradient feel
                c = (0.25, 0.10, 0.40, 0.96) if theme == "dark" else (0.90, 0.85, 0.98, 0.96)
            else:
                c = (0.15, 0.10, 0.25, 0.96) if theme == "dark" else (0.85, 0.80, 0.90, 0.96)
            Color(*c)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(22)])
        self.bind(size=self._redraw, pos=self._redraw)

    def _redraw(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size


class GameOverScreen(FloatLayout):
    """
    Game Over screen shown when no moves are left.
    Displays final score and allows restarting.
    """

    def __init__(self, score=0, best_score=0, theme="dark",
                 on_restart=None, on_menu=None, **kwargs):
        super().__init__(**kwargs)
        self.score = score
        self.best_score = best_score
        self.theme = theme
        self.on_restart_callback = on_restart
        self.on_menu_callback = on_menu

        self._bg_color_instr = None
        self._setup_ui()
        self._setup_gradient()
        Clock.schedule_once(self._animate_in, 0.1)

    def _setup_ui(self):
        with self.canvas.before:
            # Semi-transparent dark overlay
            Color(0, 0, 0, 0.65)
            self._overlay = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Card
        self.card = OverlayCard(
            theme=self.theme,
            win=False,
            size_hint=(None, None),
        )
        self.add_widget(self.card)

        # Content labels
        accent = (0.85, 0.20, 0.20, 1) if self.theme == "dark" else (0.75, 0.15, 0.15, 1)
        text_color = (0.95, 0.95, 1.0, 1) if self.theme == "dark" else (0.20, 0.15, 0.35, 1)
        score_color = (1.0, 0.75, 0.20, 1)

        self.emoji_lbl = Label(
            text="...",
            font_size="60sp",
            size_hint=(None, None),
            size=(dp(100), dp(80)),
        )

        self.title_lbl = Label(
            text="Game Over!",
            font_size="34sp",
            bold=True,
            color=accent,
            size_hint=(None, None),
            size=(dp(300), dp(50)),
        )

        self.score_lbl = Label(
            text=f"Score: {self.score}",
            font_size="24sp",
            bold=True,
            color=score_color,
            size_hint=(None, None),
            size=(dp(300), dp(40)),
        )

        self.best_lbl = Label(
            text=f"Best: {self.best_score}",
            font_size="18sp",
            color=text_color,
            size_hint=(None, None),
            size=(dp(300), dp(36)),
        )

        is_new_best = self.score >= self.best_score and self.score > 0
        if is_new_best:
            self.new_best_lbl = Label(
                text="New Best Score!",
                font_size="18sp",
                bold=True,
                color=(1.0, 0.85, 0.20, 1),
                size_hint=(None, None),
                size=(dp(300), dp(36)),
            )
        else:
            self.new_best_lbl = Label(text="", size_hint=(None, None), size=(dp(300), dp(10)))

        # Buttons
        btn_style = {
            "size_hint": (None, None),
            "size": (dp(140), dp(48)),
            "bold": True,
            "font_size": "16sp",
        }

        self.restart_btn = Button(
            text="Play Again",
            background_normal="", background_color=[0.38, 0.10, 0.72, 1],
            **btn_style,
        )
        self.restart_btn.bind(on_press=self._on_restart)

        self.menu_btn = Button(
            text="Menu",
            background_normal="", background_color=[0.20, 0.12, 0.42, 1],
            **btn_style,
        )
        self.menu_btn.bind(on_press=self._on_menu)

        for w in [self.emoji_lbl, self.title_lbl, self.score_lbl,
                   self.best_lbl, self.new_best_lbl, self.restart_btn, self.menu_btn]:
            self.add_widget(w)

        self.bind(size=self._layout, pos=self._layout)

    def _layout(self, *args):
        w, h = self.size
        px, py = self.pos
        cx = px + w / 2

        card_w = min(w - dp(40), dp(320))
        card_h = dp(370)
        self.card.size = (card_w, card_h)
        card_x = cx - card_w / 2
        card_y = py + (h - card_h) / 2
        self.card.pos = (card_x, card_y)

        # Stack content inside card
        top = card_y + card_h - dp(20)

        self.emoji_lbl.center_x = cx
        top -= dp(80)
        self.emoji_lbl.top = top + dp(80)

        self.title_lbl.center_x = cx
        top -= dp(56)
        self.title_lbl.top = top + dp(56)

        self.score_lbl.center_x = cx
        top -= dp(48)
        self.score_lbl.top = top + dp(48)

        self.best_lbl.center_x = cx
        top -= dp(44)
        self.best_lbl.top = top + dp(44)

        self.new_best_lbl.center_x = cx
        top -= dp(40)
        self.new_best_lbl.top = top + dp(40)

        top -= dp(20)
        self.restart_btn.center_x = cx - dp(78)
        self.restart_btn.top = top
        self.menu_btn.center_x = cx + dp(78)
        self.menu_btn.top = top

    def _update_bg(self, *args):
        self._overlay.pos = self.pos
        self._overlay.size = self.size

    def _animate_in(self, dt):
        self.card.opacity = 0
        Animation(opacity=1, duration=0.4, t="out_cubic").start(self.card)

    def _setup_gradient(self):
        pass  # No gradient on overlay screen

    def _on_restart(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(
            lambda dt: self.on_restart_callback() if self.on_restart_callback else None,
            0.15,
        )

    def _on_menu(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(
            lambda dt: self.on_menu_callback() if self.on_menu_callback else None,
            0.15,
        )


class VictoryScreen(FloatLayout):
    """
    Victory screen shown when the player reaches the 2048 tile.
    """

    def __init__(self, score=0, theme="dark",
                 on_continue=None, on_restart=None, **kwargs):
        super().__init__(**kwargs)
        self.score = score
        self.theme = theme
        self.on_continue_callback = on_continue
        self.on_restart_callback = on_restart

        self._setup_ui()
        Clock.schedule_once(self._animate_in, 0.1)

    def _setup_ui(self):
        with self.canvas.before:
            Color(0, 0, 0, 0.70)
            self._overlay = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.card = OverlayCard(
            theme=self.theme,
            win=True,
            size_hint=(None, None),
        )
        self.add_widget(self.card)

        gold = (1.0, 0.85, 0.20, 1)
        purple = (0.75, 0.30, 1.0, 1) if self.theme == "dark" else (0.58, 0.20, 0.85, 1)
        text_color = (0.95, 0.95, 1.0, 1) if self.theme == "dark" else (0.20, 0.15, 0.35, 1)

        self.emoji_lbl = Label(
            text="!!!",
            font_size="64sp",
            size_hint=(None, None),
            size=(dp(100), dp(85)),
        )

        self.title_lbl = Label(
            text="You Win!",
            font_size="38sp",
            bold=True,
            color=gold,
            size_hint=(None, None),
            size=(dp(300), dp(56)),
        )

        self.sub_lbl = Label(
            text="You reached 2048!",
            font_size="18sp",
            bold=True,
            color=purple,
            size_hint=(None, None),
            size=(dp(300), dp(36)),
        )

        self.score_lbl = Label(
            text=f"Score: {self.score}",
            font_size="22sp",
            bold=True,
            color=gold,
            size_hint=(None, None),
            size=(dp(300), dp(40)),
        )

        btn_style = {
            "size_hint": (None, None),
            "size": (dp(140), dp(48)),
            "bold": True,
            "font_size": "15sp",
        }

        self.continue_btn = Button(
            text="Keep Going",
            background_normal="", background_color=[0.18, 0.62, 0.22, 1],
            **btn_style,
        )
        self.continue_btn.bind(on_press=self._on_continue)

        self.restart_btn = Button(
            text="New Game",
            background_normal="", background_color=[0.38, 0.10, 0.72, 1],
            **btn_style,
        )
        self.restart_btn.bind(on_press=self._on_restart)

        for w in [self.emoji_lbl, self.title_lbl, self.sub_lbl,
                   self.score_lbl, self.continue_btn, self.restart_btn]:
            self.add_widget(w)

        self.bind(size=self._layout, pos=self._layout)

    def _layout(self, *args):
        w, h = self.size
        px, py = self.pos
        cx = px + w / 2

        card_w = min(w - dp(40), dp(320))
        card_h = dp(340)
        self.card.size = (card_w, card_h)
        card_x = cx - card_w / 2
        card_y = py + (h - card_h) / 2
        self.card.pos = (card_x, card_y)

        top = card_y + card_h - dp(20)

        self.emoji_lbl.center_x = cx
        top -= dp(88)
        self.emoji_lbl.top = top + dp(85)

        self.title_lbl.center_x = cx
        top -= dp(58)
        self.title_lbl.top = top + dp(58)

        self.sub_lbl.center_x = cx
        top -= dp(44)
        self.sub_lbl.top = top + dp(44)

        self.score_lbl.center_x = cx
        top -= dp(46)
        self.score_lbl.top = top + dp(46)

        top -= dp(20)
        self.continue_btn.center_x = cx - dp(78)
        self.continue_btn.top = top
        self.restart_btn.center_x = cx + dp(78)
        self.restart_btn.top = top

    def _update_bg(self, *args):
        self._overlay.pos = self.pos
        self._overlay.size = self.size

    def _animate_in(self, dt):
        self.card.opacity = 0
        Animation(opacity=1, duration=0.4, t="out_cubic").start(self.card)

    def _on_continue(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(
            lambda dt: self.on_continue_callback() if self.on_continue_callback else None,
            0.15,
        )

    def _on_restart(self, btn):
        AnimationManager.button_press(btn)
        Clock.schedule_once(
            lambda dt: self.on_restart_callback() if self.on_restart_callback else None,
            0.15,
        )