from datetime import date

from services.date_service import format_jalali_date


def test_format_jalali_date():
    result = format_jalali_date(
        date(2026, 10, 6)
    )

    assert result == "14 مهر 1405"