from canvasapi import Canvas
from textual.widgets import Tree

from lugach.core import cvutils as cvu


class CourseSelect(Tree):
    """Allows the user to select from the courses they manage."""

    _canvas: Canvas

    def __init__(self, canvas: Canvas, **kwargs):
        self._canvas = canvas
        super().__init__(label="Courses", **kwargs)

    def on_mount(self):
        courses = list(cvu.get_courses(self._canvas))
        self.root.expand()
        for course in courses:
            self.root.add_leaf(course.name, course)
