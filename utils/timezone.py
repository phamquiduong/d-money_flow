import datetime

import pytz

from settings import TIMEZONE

DEFAULT_TIMEZONE = pytz.timezone(TIMEZONE)


def now(tz: datetime.tzinfo | None = None) -> datetime.datetime:
    return datetime.datetime.now(tz or DEFAULT_TIMEZONE)
