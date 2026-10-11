
from datetime import date

from pydantic import BaseModel


class ReservationOverlapRequest(BaseModel):
    new_check_in: date
    new_check_out: date
    existing_check_in: date
    existing_check_out: date
