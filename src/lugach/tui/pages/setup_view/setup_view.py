from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Collapsible, Markdown, Static
from lugach.tui.pages.setup_view.canvas_courses_form import CourseMappingsForm
from lugach.tui.pages.setup_view.canvas_credentials_form import CanvasCredentialsForm
from lugach.tui.pages.setup_view.liberty_credentials_form import LibertyCredentialsForm
from lugach.tui.pages.setup_view.top_hat_credentials_form import TopHatCredentialsForm

WELCOME_MESSAGE = """\
# Welcome to LUGACH setup!

This wizard will walk you through the process of setting up your Canvas, \
Liberty, and Top Hat credentials to use LUGACH.
"""

CANVAS_MESSAGE = """\
First, let's check your your Canvas API credentials and set those up if they're \
not already working.
"""

LIBERTY_MESSAGE = """\
Now, we'll retrieve and verify your Liberty credentials. These will let us log \
into Top Hat in the next step.
"""

TOP_HAT_MESSAGE = """\
With the Liberty credentials from the last step, we'll now get your Top Hat \
credentials. This will be done automatically; if there is an error, press \
"Refresh" to try again.
"""

COURSE_MAPPINGS_MESSAGE = """\
The next thing to do is select the Canvas courses you would like to manage \
using the app, and connect them to Top Hat courses if desired. Use the list \
below to add the Canvas courses. Once you have selected a course, use the
dropdown to select its corresponding Top Hat course.
"""


class SetupView(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Markdown(WELCOME_MESSAGE)
        with Collapsible(title="(1) Canvas credentials", collapsed=False):
            yield Static(CANVAS_MESSAGE)
            yield CanvasCredentialsForm()
        with Collapsible(title="(2) Liberty credentials"):
            yield Static(LIBERTY_MESSAGE)
            yield LibertyCredentialsForm()
        with Collapsible(title="(3) Top Hat credentials"):
            yield Static(TOP_HAT_MESSAGE)
            yield TopHatCredentialsForm()
        with Collapsible(title="(4) Select Canvas courses"):
            yield Static(COURSE_MAPPINGS_MESSAGE)
            yield CourseMappingsForm()
