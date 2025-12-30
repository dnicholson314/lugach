from typing import cast

from canvasapi import Canvas
from canvasapi.course import Course
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import DataTable, Tree

from lugach.tui.pages.students_view.student_details import StudentDetails
from lugach.tui.widgets import CourseSelect, StudentDataTable


class StudentsView(Horizontal):
    """
    Page for viewing student information across the user's
    managed courses.
    """

    _canvas: Canvas

    def __init__(self, canvas: Canvas):
        super().__init__()
        self._canvas = canvas

    def compose(self) -> ComposeResult:
        yield CourseSelect(self._canvas)
        yield StudentDataTable()
        yield StudentDetails()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        value = event.node.data
        student_data_table = self.query_one(StudentDataTable)
        student_details = self.query_one(StudentDetails)
        if not value:
            student_data_table.course = None
            student_details.course = None
            student_details.student = None
            return

        course = cast(Course, value)
        student_data_table.course = course
        student_details.course = course

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        student_id = event.row_key.value
        student_details = self.query_one(StudentDetails)
        student_details.student = self._canvas.get_user(
            student_id, include=["last_login"]
        )
