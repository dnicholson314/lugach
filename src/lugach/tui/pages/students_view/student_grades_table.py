import asyncio
from datetime import datetime as dt
from datetime import timezone

from canvasapi.course import Course
from canvasapi.user import User
from dateutil.parser import parse
from rich.table import Table

from lugach.tui.utils import convert_iso_to_formatted_date

from textual.widgets import Static
from textual.reactive import reactive
from typing import Optional


async def _get_grades_table_for_student(student: User, course: Course) -> Table:
    """
    Returns a Rich Table object with a summary of the the provided student's
    grades in the provided course.
    """
    assignments = await asyncio.to_thread(course.get_assignments, order_by="due_at")

    table = Table(show_edge=False)
    table.add_column("Assignment", style="bold")
    table.add_column("Due At")
    table.add_column("Score")
    table.add_column("Total")

    total_score = total_points = 0
    for assignment in assignments:
        submission = await asyncio.to_thread(assignment.get_submission, student.id)
        if not submission:
            continue

        # Datetime object in UTC
        raw_due_date = assignment.due_at and parse(assignment.due_at)
        # Formatted datetime object in local timezone
        due_date = raw_due_date and convert_iso_to_formatted_date(raw_due_date)
        # We do the comparison in UTC for consistency
        styled_due_date = (
            f"[red]{due_date}[/red]"
            if not submission.score
            and not submission.submitted_at
            and raw_due_date < dt.now(timezone.utc)
            else due_date
        )

        table.add_row(
            f"[link={assignment.html_url}]{assignment.name}[/link]",
            styled_due_date,
            submission.score and f"{submission.score:.0f}",
            f"{assignment.points_possible:.0f}",
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


class StudentGradesTable(Static):
    student: reactive[Optional[User]] = reactive(None)
    course: reactive[Optional[Course]] = reactive(None)

    def __init__(self):
        super().__init__("No student found.")

    async def watch_student(self, new_student: Optional[User]):
        if not new_student or not self.course:
            self.update("No student found.")
            return

        self.loading = True
        grades_table = await _get_grades_table_for_student(new_student, self.course)
        self.update(grades_table)
        self.loading = False
