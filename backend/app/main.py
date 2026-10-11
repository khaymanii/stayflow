from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.reservation import ReservationOverlapRequest
from app.services.reservation_service import reservations_overlap

app = FastAPI(title="StayFlow API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db/health")
def database_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {"database": "connected"}


@app.post("/reservations/check-overlap")
def check_reservation_overlap(request: ReservationOverlapRequest):
    if request.new_check_in >= request.new_check_out:
        raise HTTPException(
            status_code=400,
            detail="Check-in must be before check-out.",
        )

    if request.existing_check_in >= request.existing_check_out:
        raise HTTPException(
            status_code=400,
            detail="Existing check-in must be before check-out.",
        )

    overlaps = reservations_overlap(
        new_check_in=request.new_check_in,
        new_check_out=request.new_check_out,
        existing_check_in=request.existing_check_in,
        existing_check_out=request.existing_check_out,
    )

    return {"overlaps": overlaps}
