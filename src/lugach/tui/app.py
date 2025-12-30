from canvasapi import Canvas
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from lugach.core import cvutils as cvu
from lugach.tui.pages.student_view import StudentView


class LUGACHApp(App):
    """A TUI for LUGACH."""

    _canvas: Canvas

    def __init__(self):
        super().__init__()
        self._canvas = cvu.create_canvas_object()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield StudentView(self._canvas)


def app() -> None:
    """The entrypoint for the TUI."""
    app = LUGACHApp()
    app.run()
