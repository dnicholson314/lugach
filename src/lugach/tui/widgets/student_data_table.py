import asyncio

from canvasapi.course import Course
from textual.reactive import reactive
from textual.widgets import DataTable


class StudentDataTable(DataTable):
    """View information about students in a course."""

    course: reactive[Course | None] = reactive(None)

    def __init__(self, course: Course | None = None, **kwargs):
        super().__init__(**kwargs)
        self.course = course
        self.cursor_type = "row"
        self.add_columns("Name", "ID", "Email")

    def update_course(self, new_course: Course | None):
        self.course = new_course

    async def watch_course(self, new_course: Course | None):
        self.clear()
        if not new_course:
            return

        students = await asyncio.to_thread(
            new_course.get_users, enrollment_type="student"
        )

        for student in students:
            key = student.id
            row = [
                student.name,
                getattr(student, "sis_user_id", ""),
                getattr(student, "email", ""),
            ]
            self.add_row(*row, key=key)
