from datetime import datetime as dt
from datetime import timezone
from typing import cast

from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.user import User
from dateutil.parser import parse
import requests
from rich.table import Table
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Collapsible, DataTable, Label, Select, Static
from textual.widgets.select import NoSelection

from lugach.core import thutils as thu
from lugach.tui.widgets import CourseSelect, StudentDataTable

from textual import log

LOCAL_TIMEZONE = dt.now().astimezone().tzinfo


def _convert_iso_to_formatted_date(iso: str | dt, format="%b %d, %Y"):
    """
    Take an ISO string or datetime object and convert it to a formatted date
    for display.
    """
    if isinstance(iso, str):
        iso = parse(iso)

    if iso.tzinfo is None:
        iso = iso.replace(tzinfo=timezone.utc)

    return iso.astimezone(LOCAL_TIMEZONE).strftime(format)


def _get_info_table_for_student(student: User) -> Table:
    """
    Returns a Rich Table object with information about the provided student.
    """
    info_table = Table(show_header=False, show_edge=False)
    info_table.add_column("key")
    info_table.add_column("value")
    info_table.add_row(
        "Name",
        student.name,
    )

    formatted_last_login = (
        _convert_iso_to_formatted_date(student.last_login)
        if getattr(student, "last_login", None)
        else ""
    )
    info_table.add_row("ID", getattr(student, "sis_user_id", ""))
    info_table.add_row("Email", getattr(student, "email", ""))
    info_table.add_row("Last active", formatted_last_login)

    return info_table


def _get_grades_table_for_student(student: User, course: Course) -> Table:
    """
    Returns a Rich Table object with a summary of the the provided student's
    grades in the provided course.
    """
    assignments = course.get_assignments(order_by="due_at")

    table = Table(show_edge=False)
    table.add_column("Assignment", style="bold")
    table.add_column("Due At")
    table.add_column("Score")
    table.add_column("Total")

    total_score = total_points = 0
    for assignment in assignments:
        submission = assignment.get_submission(student.id)
        if not submission:
            continue

        log(submission.__repr__)

        # Datetime object in UTC
        raw_due_date = assignment.due_at and parse(assignment.due_at)
        # Formatted datetime object in local timezone
        due_date = raw_due_date and _convert_iso_to_formatted_date(raw_due_date)
        # We do the comparison in UTC for consistency
        style = (
            "red"
            if not submission.submitted_at and raw_due_date < dt.now(timezone.utc)
            else None
        )

        table.add_row(
            assignment.name,
            due_date,
            submission.score and f"{submission.score:.0f}",
            f"{assignment.points_possible:.0f}",
            style=style,
        )
        total_score += round(submission.score) if submission.score else 0
        total_points += round(assignment.points_possible)

    table.add_section()
    table.add_row(
        "Grand total",
        None,
        f"{total_score:.0f}",
        f"{total_points:.0f}",
        style="bold",
    )

    return table


def _get_attendance_table_for_student(
    th_student: thu.Student, th_course: thu.Course, auth_header: thu.AuthHeader
) -> Table:
    attendance_records = thu.get_attendance_records_for_student_in_course(
        th_course, th_student, auth_header
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


class StudentDetails(Vertical):
    """
    View details about a student's status in a course.
    """

    # A flag which allows Top Hat testing in development environments.
    _development = True

    _auth_header: thu.AuthHeader
    course: reactive[Course | None] = reactive(None)
    th_course: thu.Course | None
    student: reactive[User | None] = reactive(None, recompose=True)
    th_student: thu.Student | None

    def __init__(self):
        super().__init__()
        self._auth_header = thu.get_auth_header_for_session()

    def compose(self) -> ComposeResult:
        if not self.student or not self.course:
            yield Label("No student selected.")
            return

        with Collapsible(title="Info", collapsed=False):
            yield Static(_get_info_table_for_student(self.student))
        with Collapsible(title="Grades"):
            yield Static(_get_grades_table_for_student(self.student, self.course))
        with Collapsible(title="Attendance"):
            if not self.th_student or not self.th_course:
                yield Label(
                    f"No Top Hat records could be found for {self.student.name}."
                )
            else:
                yield Static(
                    _get_attendance_table_for_student(
                        th_student=self.th_student,
                        th_course=self.th_course,
                        auth_header=self._auth_header,
                    )
                )

    async def watch_course(self, new_course: Course | None):
        if not new_course:
            self.th_course = None
            return

        th_courses = thu.get_th_courses(self._auth_header)

        if self._development:
            matches = (
                course
                for course in th_courses
                if course.get("course_name") == "Test Course 1"
            )
            self.th_course = next(matches, None)
            return

        for course in th_courses:
            id = course.get("course_id")
            if not id:
                continue

            lti_data: dict = {}
            try:
                lti_url = f"https://app.tophat.com/api/v3/sync/courses/{id}/config/"
                lti_response = requests.get(lti_url, headers=self._auth_header)
                lti_response.raise_for_status()
                lti_data = lti_response.json()
            except requests.HTTPError:
                continue

            cv_course_id = lti_data.get("lms_course_id")
            if not cv_course_id or cv_course_id != new_course.id:
                continue

            self.th_course = course
            return

    async def watch_student(self, new_student: User | None):
        if not new_student or not self.th_course:
            self.th_student = None
            return

        email = new_student.email
        th_students = thu.get_th_students(self._auth_header, self.th_course)

        matches = (student for student in th_students if student["email"] == email)
        self.th_student = next(matches, None)


class StudentView(Horizontal):
    """
    Page for viewing student information across the user's
    managed courses.
    """

    _canvas: Canvas

    def __init__(self, canvas: Canvas):
        super().__init__()
        self._canvas = canvas

    def compose(self) -> ComposeResult:
        with Vertical():
            yield CourseSelect(self._canvas)
            yield StudentDataTable()
        yield StudentDetails()

    def on_select_changed(self, event: Select.Changed) -> None:
        value = event.value
        student_data_table = self.query_one(StudentDataTable)
        student_details = self.query_one(StudentDetails)

        if isinstance(value, NoSelection):
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
