from enum import Enum

from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Label


class Status(Enum):
    VALID = "success"
    INVALID = "warning"
    ERROR = "error"
    NOT_FOUND = "secondary"


def _get_icon_from_status(status: Status) -> str:
    match status:
        case Status.VALID:
            return ":white_check_mark:"
        case Status.INVALID:
            return ":warning:"
        case Status.ERROR:
            return ":x:"
        case Status.NOT_FOUND:
            return ":heavy_minus_sign:"


class StatusLabel(Label):
    status: reactive[Status] = reactive(Status.ERROR)

    def __init__(self, title: str):
        super().__init__()
        self.border_title = title

    def watch_status(self, next_status: Status) -> None:
        icon = _get_icon_from_status(next_status)
        description = ""
        match next_status:
            case Status.VALID:
                description = "Valid"
            case Status.INVALID:
                description = "Invalid"
            case Status.ERROR:
                description = "Could not verify status"
            case Status.NOT_FOUND:
                description = "Not found"
        text = Text.from_markup(f"{icon}  {description}")
        self.update(text)
        self.set_classes(next_status.value)
