import datetime as dt

import pytest

from src.services.utils import get_start_date


def test_get_start_date():
    as_of_date = dt.date(2023, 9, 6)
    start_date_exp = dt.date(2023, 9, 5)

    start_date_actual = get_start_date(as_of_date)
    assert start_date_exp == start_date_actual


if __name__ == "__main__":
    pytest.main([__file__])
