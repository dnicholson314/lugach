from canvasapi import Canvas
from textual.app import App, ComposeResult
from textual.widgets import Footer

from lugach.core import cvutils as cvu
from lugach.tui.pages.students_view import StudentsView
from lugach.tui.pages.setup_view import SetupView


class LUGACHApp(App):
    """A TUI for LUGACH."""

    _canvas: Canvas
    CSS_PATH = "app.tcss"

    def __init__(self):
        super().__init__()
        self.title = "LUGACH"
        # self._canvas = cvu.create_canvas_object()

    def compose(self) -> ComposeResult:
        yield Footer()
        yield SetupView()
        # yield StudentsView(self._canvas)


def app() -> None:
    """The entrypoint for the TUI."""
    app = LUGACHApp()
    app.run()


if __name__ == "__main__":
    app()
