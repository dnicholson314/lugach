from canvasapi.course import Course
from canvasapi.user import User
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Collapsible

from lugach.core import thutils as thu
from lugach.tui.pages.students_view.student_attendance_table import (
    StudentAttendanceTable,
)
from lugach.tui.pages.students_view.student_info_table import StudentInfoTable
from lugach.tui.pages.students_view.student_grades_table import StudentGradesTable


class StudentDetails(Vertical):
    """
    View details about a student's status in a course.
    """

    _auth_header: thu.AuthHeader
    course: reactive[Course | None] = reactive(None)
    student: reactive[User | None] = reactive(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._auth_header = thu.get_auth_header_for_session()

    def compose(self) -> ComposeResult:
        with Collapsible(title="Info", collapsed=False):
            yield StudentInfoTable().data_bind(StudentDetails.student)
        with Collapsible(title="Grades"):
            yield StudentGradesTable().data_bind(
                StudentDetails.course, StudentDetails.student
            )
        with Collapsible(title="Attendance"):
            yield StudentAttendanceTable().data_bind(
                StudentDetails.course, StudentDetails.student
            )
