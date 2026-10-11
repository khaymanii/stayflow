from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ReservationCreate(BaseModel):
    check_in: date
    check_out: date


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    check_in: date
    check_out: date
    created_at: datetime


class ReservationOverlapRequest(BaseModel):
    new_check_in: date
    new_check_out: date
    existing_check_in: date
    existing_check_out: date
