from canvasapi.course import Course
from canvasapi.user import User
from textual import work
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable, Input
from textual.app import ComposeResult

from typing import Optional

from pyperclip import copy
from textual.worker import Worker

import asyncio


class StudentsDataTable(DataTable):
    """View and select students from a course."""

    course: reactive[Course | None] = reactive(None)

    BINDINGS = [("e", "copy_email()", "Copy email")]

    def __init__(self, course: Course | None = None, **kwargs):
        super().__init__(**kwargs)
        self.course = course
        self.cursor_type = "row"
        self.students: list[User] = []
        self.add_columns("Name", "ID", "Email")

    def update_data(self, next_data: list[User]):
        self.clear()
        for student in next_data:
            key = student.id
            row = [
                student.name,
                getattr(student, "sis_user_id", ""),
                getattr(student, "email", ""),
            ]
            self.add_row(*row, key=key)

    @work(exclusive=True)
    async def load_students(self, course: Course) -> list[User]:
        paginated_students = await asyncio.to_thread(
            course.get_users, enrollment_type="student"
        )
        return await asyncio.to_thread(list, paginated_students)

    def watch_course(self, new_course: Course | None):
        if not new_course:
            self.clear()
            return

        self.loading = True
        self.load_students(new_course)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if (
            not event.worker.name == "load_students"
            or event.worker.is_cancelled
            or not event.worker.is_finished
        ):
            return

        if not event.worker.result:
            self.notify("Failed to load students from course.", severity="error")
            return

        students: list[User] = event.worker.result

        self.students = students
        self.update_data(students)
        self.loading = False

    def action_copy_email(self) -> None:
        EMAIL_INDEX = 2
        email = self.get_row_at(self.cursor_row)[EMAIL_INDEX]
        if email:
            copy(email)


class SearchableStudentsDataTable(Vertical):
    """Extends `StudentsDataTable` by adding searching."""

    course: reactive[Course | None] = reactive(None)
    last_row_selected_id: Optional[str] = None

    class SelectionLost(Message):
        """Fires when the user's selection has been lost due to a query."""

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Name")
        yield StudentsDataTable().data_bind(SearchableStudentsDataTable.course)

    def on_input_changed(self, event: Input.Changed):
        value = event.value
        self.filter_students(value)

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        self.last_row_selected_id = event.row_key.value

    def filter_students(self, query: str) -> None:
        students_data_table = self.query_one(StudentsDataTable)
        if not query:
            students_data_table.update_data(students_data_table.students)
            return

        query = query.lower()
        filtered_students = [
            student
            for student in students_data_table.students
            if query in student.name.lower()
        ]
        students_data_table.update_data(filtered_students)

        if not self.last_row_selected_id:
            return

        selected_student_matches = (
            student
            for student in filtered_students
            if student.id == self.last_row_selected_id
        )
        selected_student = next(selected_student_matches, None)
        if not selected_student:
            self.post_message(self.SelectionLost())
