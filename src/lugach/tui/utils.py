from datetime import datetime as dt
from datetime import timezone

from dateutil.parser import parse

LOCAL_TIMEZONE = dt.now().astimezone().tzinfo


def convert_iso_to_formatted_date(iso: str | dt, format="%b %d, %Y"):
    """
    Take an ISO string or datetime object and convert it to a formatted date
    for display.
    """
    if isinstance(iso, str):
        iso = parse(iso)

    if iso.tzinfo is None:
        iso = iso.replace(tzinfo=timezone.utc)

    return iso.astimezone(LOCAL_TIMEZONE).strftime(format)
