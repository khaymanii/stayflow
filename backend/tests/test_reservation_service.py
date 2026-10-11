from datetime import date

from app.services.reservation_service import reservations_overlap


def test_overlapping_reservations():
    result = reservations_overlap(
        date(2026, 10, 8),
        date(2026, 10, 10),
        date(2026, 10, 5),
        date(2026, 10, 12),
    )

    assert result is True


def test_back_to_back_reservations_do_not_overlap():
    result = reservations_overlap(
        date(2026, 10, 15),
        date(2026, 10, 18),
        date(2026, 10, 10),
        date(2026, 10, 15),
    )

    assert result is False