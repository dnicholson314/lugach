from getpass import getpass
from lugach.core.secrets import get_credentials, set_credentials, remove_credentials

LIBERTY_CREDENTIALS_ID = "LU_LIGHTHOUSE"


def get_liberty_credentials() -> tuple[str, str]:
    LIBERTY_CREDENTIALS = get_credentials(LIBERTY_CREDENTIALS_ID)
    return LIBERTY_CREDENTIALS


def get_liberty_username() -> str | None:
    try:
        return get_credentials(LIBERTY_CREDENTIALS_ID)[0]
    except NameError:
        return None


def update_liberty_credentials(username: str, password: str) -> None:
    set_credentials(id=LIBERTY_CREDENTIALS_ID, username=username, password=password)


def revoke_liberty_credentials() -> None:
    remove_credentials(LIBERTY_CREDENTIALS_ID)


def prompt_user_for_liberty_credentials():
    username = input("Enter your Liberty username: ")
    password = getpass("Enter your Liberty password: ")
    update_liberty_credentials(username, password)
