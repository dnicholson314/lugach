import asyncio
from typing import Optional

from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.user import User
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import DataTable, Tree

from lugach.tui.pages.students_view.student_details import StudentDetails
from lugach.tui.widgets import CourseSelect, SearchableStudentsDataTable


class StudentsView(Horizontal):
    """
    Page for viewing student information across the user's
    managed courses.
    """

    _canvas: Canvas
    course: reactive[Optional[Course]] = reactive(None)
    student: reactive[Optional[User]] = reactive(None)

    def __init__(self, canvas: Canvas):
        super().__init__()
        self._canvas = canvas

    def compose(self) -> ComposeResult:
        yield CourseSelect(self._canvas)
        yield SearchableStudentsDataTable().data_bind(StudentsView.course)
        yield StudentDetails().data_bind(StudentsView.course, StudentsView.student)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        value = event.node.data
        if self.course == value:
            return

        self.course = value if value else None
        self.student = None

    async def on_data_table_row_selected(self, event: DataTable.RowSelected):
        student_id = event.row_key.value
        self.student = await asyncio.to_thread(
            self._canvas.get_user, student_id, include=["last_login"]
        )

    @on(SearchableStudentsDataTable.SelectionLost)
    async def on_selection_lost(self):
        self.student = None
