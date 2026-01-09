import asyncio
from textual import work
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.reactive import reactive
from textual.widgets import Button

from lugach.tui.widgets.status_label import Status, StatusLabel

from lugach.core import thutils as thu

from playwright.sync_api import sync_playwright


def _verify_top_hat_credentials() -> Status:
    with sync_playwright() as playwright:
        try:
            thu.get_auth_header_for_session()
            return Status.VALID
        except (NameError, ConnectionRefusedError):
            pass
        except Exception:
            return Status.ERROR

        print(
            "The saved Top Hat credentials did not work, attempting to",
            "obtain new credentials...",
        )
        try:
            thu.refresh_th_auth_key(playwright)
            return Status.VALID
        except PermissionError:
            pass
        except Exception:
            return Status.ERROR

        print(
            "Could not access Top Hat automatically; loading Top Hat",
            "using Liberty credentials and trying again...",
        )
        try:
            thu.get_th_storage_state(playwright)
            thu.refresh_th_auth_key(playwright)
        except PermissionError:
            pass
        except Exception:
            return Status.ERROR

    return Status.INVALID


class TopHatCredentialsForm(VerticalGroup):
    status: reactive[Status] = reactive(Status.ERROR)

    def compose(self) -> ComposeResult:
        with HorizontalGroup(classes="cv_creds_buttons"):
            yield StatusLabel("Top Hat Credentials").data_bind(
                TopHatCredentialsForm.status
            )
            yield Button(label="Refresh", variant="primary")

    @work(exclusive=True)
    async def update_status(self, refreshed=False):
        status_label = self.query_one(StatusLabel)
        status_label.loading = True
        self.status = await asyncio.to_thread(_verify_top_hat_credentials)
        status_label.loading = False
        if refreshed:
            self.notify("Status refreshed.")

    def on_mount(self) -> None:
        self.update_status()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        label = event.button.label
        if label == "Refresh":
            self.update_status(refreshed=True)
