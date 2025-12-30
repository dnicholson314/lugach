from canvasapi import Canvas
from canvasapi.course import Course
from textual.widgets import Select

from lugach.core import cvutils as cvu


class CourseSelect(Select[Course]):
    """Allows the user to select from the courses they manage."""

    _canvas: Canvas

    def __init__(self, canvas: Canvas, **kwargs):
        self._canvas = canvas
        courses = list(cvu.get_courses(self._canvas))
        options = [(course.name, course) for course in courses]
        super().__init__(options, **kwargs)
