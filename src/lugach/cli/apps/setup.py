from getpass import getpass
from canvasapi.exceptions import InvalidAccessToken
from playwright.sync_api import sync_playwright
import lugach.core.cvutils as cvu
from lugach.core.secrets import update_env_file
import lugach.core.thutils as thu

import warnings

warnings.filterwarnings("ignore")

WELCOME_MESSAGE = """\
    Welcome to LUGACH! This application will walk you through the steps
    necessary to connect Canvas and Top Hat to LUGACH and get the
    program running as intended.

    Press ENTER to continue or (q) to quit. \
"""

CANVAS_MESSAGE = """\
    First, we'll check to see if you created an .env file and added
    your Canvas API key. If not, we'll go ahead and do those things.\
"""

CHROMIUM_MESSAGE = """\
    Next, we'll make sure the Chromium browser is installed for Playwright,
    which is needed to authenticate with Top Hat.\
"""

TOP_HAT_MESSAGE = """\
    Finally, we'll check if your Top Hat credentials work,
    and log you in via a browser window if needed.\
"""

SETUP_COMPLETE = """\
    You're all done with setup!

    Press ENTER to quit.
"""


def _update_canvas_credentials() -> None:
    api_url = input("Enter the Canvas API url: ")
    api_key = getpass("Enter the Canvas API key: ")
    update_env_file(CANVAS_API_URL=api_url, CANVAS_API_KEY=api_key)


def _set_up_canvas_api_key():
    while True:
        try:
            cvu.create_canvas_object()

            should_update_canvas_credentials = input(
                "    The provided Canvas credentials work! Would you like to update them (y/n)? "
            )
            if should_update_canvas_credentials == "y":
                _update_canvas_credentials()

            return
        except (NameError, InvalidAccessToken):
            print("    The provided credentials were incorrect.")
            _update_canvas_credentials()


def _set_up_chromium():
    print("    Checking Chromium browser installation...")
    success = thu.ensure_chromium_installed()
    if success:
        print("    Chromium is ready!")
    else:
        print(
            "    Warning: Failed to verify or install Chromium. Playwright login may fail."
        )


def _update_top_hat_credentials():
    print(
        "    Opening a browser window for Top Hat login...\n"
        "    Please log in using your school account (and complete any MFA prompts if needed).\n"
        "    The browser will close automatically once authentication succeeds."
    )
    with sync_playwright() as playwright:
        try:
            thu.login_to_top_hat(playwright)
            print("    Successfully logged into Top Hat!")
        except Exception as e:
            print(f"    Failed to authenticate with Top Hat: {e}")


def _set_up_th_auth_key():
    while True:
        try:
            thu.get_auth_header_for_session()
            should_update_top_hat_credentials = input(
                "    The provided Top Hat credentials work! Would you like to update them (y/n)? "
            )
            if should_update_top_hat_credentials == "y":
                _update_top_hat_credentials()
            return
        except (NameError, ConnectionRefusedError):
            print("    Top Hat credentials are not set up or have expired.")
            _update_top_hat_credentials()
            try:
                thu.get_auth_header_for_session()
                return
            except (NameError, ConnectionRefusedError):
                retry = input(
                    "    Authentication did not complete. Would you like to try again (y/n)? "
                )
                if retry != "y":
                    return


def main():
    continue_setup = input(WELCOME_MESSAGE)
    if continue_setup == "q":
        return

    print()
    print(CANVAS_MESSAGE)
    print()

    _set_up_canvas_api_key()

    print()
    print(CHROMIUM_MESSAGE)
    print()

    _set_up_chromium()

    print()
    print(TOP_HAT_MESSAGE)
    print()

    _set_up_th_auth_key()

    print()
    input(SETUP_COMPLETE)

