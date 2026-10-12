from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.reservation import Reservation
from app.schemas.reservation import (
    ReservationCreate,
    ReservationOverlapRequest,
    ReservationResponse,
)
from app.services.reservation_service import reservations_overlap
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomResponse

app = FastAPI(title="StayFlow API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db/health")
def database_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}


@app.post(
    "/reservations",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reservation(
    request: ReservationCreate,
    db: Session = Depends(get_db),
):
    if request.check_in >= request.check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in must be before check-out.",
        )

    # Confirm that the requested room exists.
    room = db.get(Room, request.room_id)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found.",
        )

    # Look for overlapping reservations in this room only.
    statement = select(Reservation).where(
        Reservation.room_id == request.room_id,
        Reservation.check_in < request.check_out,
        Reservation.check_out > request.check_in,
    )

    existing_reservation = db.scalars(statement).first()

    if existing_reservation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This room is already reserved for those dates.",
        )

    reservation = Reservation(
        room_id=request.room_id,
        check_in=request.check_in,
        check_out=request.check_out,
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation

@app.post("/reservations/check-overlap")
def check_reservation_overlap(request: ReservationOverlapRequest):
    if request.new_check_in >= request.new_check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in must be before check-out.",
        )

    if request.existing_check_in >= request.existing_check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Existing check-in must be before check-out.",
        )

    overlaps = reservations_overlap(
        new_check_in=request.new_check_in,
        new_check_out=request.new_check_out,
        existing_check_in=request.existing_check_in,
        existing_check_out=request.existing_check_out,
    )

    return {"overlaps": overlaps}


@app.get(
    "/reservations",
    response_model=list[ReservationResponse],
)
def list_reservations(
    db: Session = Depends(get_db),
):
    statement = select(Reservation).order_by(Reservation.id)
    reservations = db.scalars(statement).all()

    return reservations


@app.get(
    "/reservations/{reservation_id}",
    response_model=ReservationResponse,
)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = db.get(Reservation, reservation_id)

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found.",
        )

    return reservation


@app.delete(
    "/reservations/{reservation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = db.get(Reservation, reservation_id)

    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found.",
        )

    db.delete(reservation)
    db.commit()

    return None

@app.post(
    "/rooms",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_room(
    request: RoomCreate,
    db: Session = Depends(get_db),
):
    name = request.name.strip()

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room name cannot be empty.",
        )

    existing_room = db.scalar(
        select(Room).where(Room.name == name)
    )

    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A room with this name already exists.",
        )

    room = Room(name=name)
    db.add(room)
    db.commit()
    db.refresh(room)

    return room


@app.get("/rooms", response_model=list[RoomResponse])
def list_rooms(db: Session = Depends(get_db)):
    statement = select(Room).order_by(Room.id)
    return db.scalars(statement).all()
