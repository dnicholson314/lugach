from typing import Optional
from canvasapi.user import User
from textual.widgets import Static

from rich.table import Table

from textual.reactive import reactive

from lugach.tui.utils import convert_iso_to_formatted_date


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
        convert_iso_to_formatted_date(student.last_login)
        if getattr(student, "last_login", None)
        else ""
    )
    info_table.add_row("ID", getattr(student, "sis_user_id", ""))
    info_table.add_row("Email", getattr(student, "email", ""))
    info_table.add_row("Last active", formatted_last_login)

    return info_table


class StudentInfoTable(Static):
    student: reactive[Optional[User]] = reactive(None)

    def __init__(self):
        super().__init__("No student found.")

    def watch_student(self, new_student: Optional[User]):
        if not new_student:
            self.update("No student found.")
            return

        self.loading = True
        info_table = _get_info_table_for_student(new_student)
        self.update(info_table)
        self.loading = False
