import asyncio
from typing import Optional

from canvasapi.course import Course
from canvasapi.user import User
from rich.table import Table
from textual import work
from textual.reactive import reactive
from textual.widgets import Static


from lugach.core import thutils as thu


async def _get_attendance_table_for_student(
    th_student: thu.Student, th_course: thu.Course, auth_header: thu.AuthHeader
) -> Table:
    attendance_records = await asyncio.to_thread(
        thu.get_attendance_records_for_student_in_course,
        th_course,
        th_student,
        auth_header,
    )
    table = Table(show_edge=False)
    table.add_column("Date", style="bold")
    table.add_column("Status")

    for record in attendance_records:
        if record["excused"]:
            status = "Excused ℹ️"
        elif record["attended"]:
            status = "Present ✅"
        else:
            status = "Absent ❌"

        table.add_row(
            record["date_taken"].isoformat(),
            status,
        )

    return table


class StudentAttendanceTable(Static):
    student: reactive[Optional[User]] = reactive(None)
    course: reactive[Optional[Course]] = reactive(None)
    th_course: Optional[thu.Course] = None
    _auth_header: thu.AuthHeader

    def __init__(self):
        super().__init__("No student selected.")
        self._auth_header = thu.get_auth_header_for_session()

    @work(exclusive=True)
    async def update_th_course(self, cv_course: Optional[Course]):
        if not cv_course:
            self.th_course = None
            return

        self.th_course = await asyncio.to_thread(
            thu.get_th_course_from_canvas_course,
            auth_header=self._auth_header,
            cv_course=cv_course,
            development=True,
        )

    @work(exclusive=True)
    async def update_th_student(self, cv_student: Optional[User]):
        if not cv_student or not self.th_course:
            self.update("No student selected.")
            return

        self.loading = True
        email = cv_student.email
        th_students = await asyncio.to_thread(
            thu.get_th_students, auth_header=self._auth_header, course=self.th_course
        )

        matches = (student for student in th_students if student["email"] == email)
        new_th_student = next(matches, None)
        if not new_th_student:
            self.update("Could not retrieve attendance records for this student.")
            self.loading = False
            return

        attendance_table = await _get_attendance_table_for_student(
            new_th_student, self.th_course, self._auth_header
        )
        self.update(attendance_table)
        self.loading = False

    async def watch_course(self, new_course: Optional[Course]):
        self.update_th_course(new_course)

    async def watch_student(self, new_student: Optional[User]):
        self.update_th_student(new_student)
