import asyncio
from canvasapi.requester import InvalidAccessToken
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Button, Input

from lugach.tui.widgets.status_label import Status, StatusLabel


from lugach.core import cvutils as cvu


def _verify_canvas_credentials() -> Status:
    """Verifies whether the user's canvas credentials are valid."""
    try:
        cvu.create_canvas_object()
        return Status.VALID
    except InvalidAccessToken:
        return Status.INVALID
    except NameError:
        return Status.NOT_FOUND
    except Exception:
        return Status.ERROR


class CanvasCredentialsForm(VerticalGroup):
    status: reactive[Status] = reactive(Status.ERROR)

    def compose(self) -> ComposeResult:
        with HorizontalGroup(classes="cv_creds_buttons"):
            yield StatusLabel("Canvas Credentials").data_bind(
                CanvasCredentialsForm.status
            )
            yield Button(label="Update", variant="primary")
            yield Button(
                label="Revoke",
                variant="error",
                id="cv_revoke_button",
            )
            yield Button(label="Refresh", variant="primary")
        yield Input(
            placeholder="API URL", classes="cv_creds_field", id="cv_api_url_input"
        )
        yield Input(
            placeholder="API key",
            classes="cv_creds_field",
            id="cv_api_key_input",
            password=True,
        )

    def on_mount(self) -> None:
        self.update_status()

    def update_status(self) -> None:
        self.status = _verify_canvas_credentials()
        revoke_button = self.query_one("#cv_revoke_button", Button)
        api_url_input = self.query_one("#cv_api_url_input", Input)
        api_key_input = self.query_one("#cv_api_key_input", Input)
        revoke_button.disabled = self.status == Status.NOT_FOUND
        api_url_input.value = cvu.get_canvas_url() or ""
        api_key_input.value = ""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        label = event.button.label
        if label == "Refresh":
            self.update_status()
            self.notify("Status refreshed.")
        elif label == "Revoke":
            await asyncio.to_thread(cvu.revoke_canvas_credentials)
            self.update_status()
            self.notify("Token revoked!")
        elif label == "Update":
            api_url_input = self.query_one("#cv_api_url_input", Input)
            api_key_input = self.query_one("#cv_api_key_input", Input)
            if not api_url_input.value or not api_key_input.value:
                self.notify(
                    "Please provide a Canvas API URL and key.", severity="error"
                )
                return

            cvu.update_canvas_credentials(api_url_input.value, api_key_input.value)
            self.update_status()
            self.notify("Token updated!")
