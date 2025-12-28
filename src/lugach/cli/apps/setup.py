from getpass import getpass
from canvasapi.exceptions import InvalidAccessToken
from playwright.sync_api import sync_playwright
import lugach.core.cvutils as cvu
from lugach.core.secrets import update_env_file
import lugach.core.thutils as thu
import lugach.core.flutils as flu

import warnings

warnings.filterwarnings("ignore")

WELCOME_MESSAGE = """\
    Welcome to LUGACH! This application will walk you through the steps
    necessary to connect Canvas and Lighthouse to LUGACH and get the
    program running as intended.

    Press ENTER to continue or (q) to quit. \
"""

CANVAS_MESSAGE = """\
    First, we'll check to see if you created an .env file and added
    your Canvas API key. If not, we'll go ahead and do those things.\
"""

LIBERTY_CREDENTIALS_MESSAGE = """\
    Next, we'll check if you have inputted proper Liberty credentials,
    which are required to set up Top Hat.\
"""

TOP_HAT_MESSAGE = """\
    Finally, we'll go ahead and check if your Top Hat credentials work,
    and retrieve them if not.\
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


def _set_up_liberty_credentials():
    while True:
        try:
            flu.get_liberty_credentials()
            should_update_liberty_credentials = input(
                "    The provided Liberty credentials work! Would you like to update them (y/n)? "
            )
            if should_update_liberty_credentials == "y":
                flu.prompt_user_for_liberty_credentials()

            return
        except NameError:
            print("    Failed to obtain Liberty credentials.")
            flu.prompt_user_for_liberty_credentials()


def _update_top_hat_credentials():
    with sync_playwright() as playwright:
        try:
            th_auth_key = thu.refresh_th_auth_key(playwright)
            update_env_file(**{thu.AUTH_KEY_SECRET_NAME: th_auth_key})
            return
        except PermissionError:
            pass

        print(
            "    Could not access Top Hat automatically; loading Top Hat using Liberty credentials "
            "\n    and trying again..."
        )
        thu.get_th_storage_state(playwright)
        th_auth_key = thu.refresh_th_auth_key(playwright)
        update_env_file(**{thu.AUTH_KEY_SECRET_NAME: th_auth_key})


def _set_up_th_auth_key():
    while True:
        try:
            thu.get_auth_header_for_session()
            print("    The provided Top Hat credentials work!")
            return
        except (NameError, ConnectionRefusedError):
            should_update_top_hat_credentials = input(
                "    The provided Top Hat credentials did not work. Would you like to try updating them"
                "\nautomatically (y/n)? "
            )
            if should_update_top_hat_credentials != "y":
                return

            _update_top_hat_credentials()


def main():
    continue_setup = input(WELCOME_MESSAGE)
    if continue_setup == "q":
        return

    print()
    print(CANVAS_MESSAGE)
    print()

    _set_up_canvas_api_key()

    print()
    print(LIBERTY_CREDENTIALS_MESSAGE)
    print()

    _set_up_liberty_credentials()

    print()
    print(TOP_HAT_MESSAGE)
    print()

    _set_up_th_auth_key()

    print()
    input(SETUP_COMPLETE)
