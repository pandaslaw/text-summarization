import datetime as dt

import pytest

from src.services.utils import get_start_date


def test_get_start_date():
    as_of_date = dt.date(2023, 9, 6)
    start_date_exp = dt.date(2023, 9, 5)

    start_date_actual = get_start_date(as_of_date)
    assert start_date_exp == start_date_actual


@pytest.mark.asyncio
async def test_generate_summary_for_topic(bot_app):
    topic = "BTC"
    result = await generate_summary_for_topic(bot_app, topic)
    assert result is not None
    assert "summary" in result


if __name__ == "__main__":
    pytest.main([__file__])
