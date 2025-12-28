from getpass import getpass
from lugach.core.secrets import get_credentials, set_credentials

LIBERTY_CREDENTIALS_ID = "LU_LIGHTHOUSE"


def get_liberty_credentials() -> tuple[str, str]:
    LIBERTY_CREDENTIALS = get_credentials(LIBERTY_CREDENTIALS_ID)
    return LIBERTY_CREDENTIALS


def prompt_user_for_liberty_credentials():
    username = input("Enter your Liberty username: ")
    password = getpass("Enter your Liberty password: ")
    set_credentials(id=LIBERTY_CREDENTIALS_ID, username=username, password=password)
