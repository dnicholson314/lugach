import asyncio
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.reactive import reactive
from textual.widgets import Button, Input

from lugach.core import flutils as flu
from lugach.tui.widgets.status_label import Status, StatusLabel


def verify_liberty_credentials() -> Status:
    try:
        flu.get_liberty_credentials()
        return Status.VALID
    except NameError:
        return Status.NOT_FOUND


class LibertyCredentialsForm(VerticalGroup):
    status: reactive[Status] = reactive(Status.ERROR)

    def compose(self) -> ComposeResult:
        with HorizontalGroup(classes="cv_creds_buttons"):
            yield StatusLabel("Liberty Credentials").data_bind(
                LibertyCredentialsForm.status
            )
            yield Button(label="Update", variant="primary")
            yield Button(
                label="Revoke",
                variant="error",
                id="fl_revoke_button",
            )
            yield Button(label="Refresh", variant="primary")
        yield Input(
            placeholder="Liberty username",
            classes="cv_creds_field",
            id="fl_username_input",
        )
        yield Input(
            placeholder="Liberty password",
            classes="cv_creds_field",
            id="fl_password_input",
            password=True,
        )

    def on_mount(self) -> None:
        self.update_status()

    def update_status(self) -> None:
        self.status = verify_liberty_credentials()
        revoke_button = self.query_one("#fl_revoke_button", Button)
        username_input = self.query_one("#fl_username_input", Input)
        password_input = self.query_one("#fl_password_input", Input)
        revoke_button.disabled = self.status == Status.NOT_FOUND
        username_input.value = flu.get_liberty_username() or ""
        password_input.value = ""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        label = event.button.label
        if label == "Refresh":
            self.update_status()
            self.notify("Status refreshed.")
        elif label == "Revoke":
            await asyncio.to_thread(flu.revoke_liberty_credentials)
            self.update_status()
            self.notify("Token revoked!")
        elif label == "Update":
            username_input = self.query_one("#fl_username_input", Input)
            password_input = self.query_one("#fl_password_input", Input)
            if not username_input.value or not password_input.value:
                self.notify(
                    "Please provide a Canvas API URL and key.", severity="error"
                )
                return

            flu.update_liberty_credentials(username_input.value, password_input.value)
            self.update_status()
            self.notify("Token updated!")
