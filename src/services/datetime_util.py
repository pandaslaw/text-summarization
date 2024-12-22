import datetime as dt
from datetime import datetime

import pytz
from dateutil import parser


class DatetimeUtil:
    @classmethod
    def utc_now(cls) -> dt.datetime:
        return dt.datetime.now(tz=dt.timezone.utc)

    @classmethod
    def utc_yesterday(cls) -> dt.datetime:
        now_utc = cls.utc_now()
        yesterday_utc = now_utc - dt.timedelta(days=1)
        return yesterday_utc

    @classmethod
    def parse_and_convert_to_utc(cls, date_string: str) -> dt.datetime:
        """Parse the input string (assumes it is in Eastern Time)."""
        # eastern = pytz.timezone("US/Eastern")
        # naive_datetime = parser.parse(date_string)  # Parse without timezone awareness
        # eastern_datetime = eastern.localize(
        #     naive_datetime
        # )  # Attach the Eastern timezone
        # # Convert to UTC
        # utc_datetime = eastern_datetime.astimezone(pytz.utc)
        datetime_obj = dt.datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")
        return datetime_obj
