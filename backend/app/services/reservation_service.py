from datetime import date


def reservations_overlap(
    new_check_in: date,
    new_check_out: date,
    existing_check_in: date,
    existing_check_out: date,
) -> bool:
    """Return True if two reservation periods overlap."""

    return (
        new_check_in < existing_check_out
        and new_check_out > existing_check_in
    )