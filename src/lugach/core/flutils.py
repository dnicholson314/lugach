from getpass import getpass
from lugach.core.secrets import get_credentials, set_credentials
from playwright.sync_api import Playwright

from lugach.core.secrets import ROOT_DIR

LIBERTY_CREDENTIALS_ID = "LU_LIGHTHOUSE"
TH_AUTH_FILE = ROOT_DIR / "state.json"


def get_liberty_credentials() -> tuple[str, str]:
    LIBERTY_CREDENTIALS = get_credentials(LIBERTY_CREDENTIALS_ID)
    return LIBERTY_CREDENTIALS


def prompt_user_for_liberty_credentials():
    username = input("Enter your Liberty username: ")
    password = getpass("Enter your Liberty password: ")
    set_credentials(id=LIBERTY_CREDENTIALS_ID, username=username, password=password)


def authenticate_for_th(playwright: Playwright) -> None:
    liberty_username, liberty_password = get_liberty_credentials()
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://app.tophat.com/login")
    page.get_by_role("combobox", name="Type to search for your school").click()
    page.get_by_role("combobox", name="Type to search for your school").fill(
        "Liberty University"
    )
    page.get_by_role("option", name="Liberty University", exact=True).click()
    page.get_by_role("button", name="Log in with school account").click()
    page.get_by_role("textbox", name="Enter your email, phone, or").click()
    page.get_by_role("textbox", name="Enter your email, phone, or").fill(
        liberty_username
    )
    page.get_by_role("button", name="Next").click()
    page.get_by_role("textbox", name="Enter the password for").click()
    page.get_by_role("textbox", name="Enter the password for").fill(liberty_password)
    page.get_by_role("button", name="Sign in").click()

    page.wait_for_url("**/e")

    context.storage_state(path=TH_AUTH_FILE)

    context.close()
    browser.close()
