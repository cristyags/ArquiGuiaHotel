from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.reservation import Reservation
from app.models.room import Room


def get_all(db: Session) -> list[Room]:
    return db.query(Room).order_by(Room.room_number.asc()).all()


def get_available(db: Session) -> list[Room]:
    return db.query(Room).filter(Room.status == "available").order_by(Room.room_number.asc()).all()


def get_by_id(db: Session, room_id: int) -> Room | None:
    return db.query(Room).filter(Room.id == room_id).first()


def create(db: Session, data_dict: dict) -> Room | None:
    room = Room(**data_dict)
    db.add(room)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(room)
    return room


def update(db: Session, room: Room, data_dict: dict) -> Room | None:
    for key, value in data_dict.items():
        if value is not None:
            setattr(room, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(room)
    return room


def update_status(db: Session, room: Room, new_status: str) -> Room:
    room.status = new_status
    db.commit()
    db.refresh(room)
    return room


def has_reservations(db: Session, room_id: int) -> bool:
    return db.query(Reservation).filter(Reservation.room_id == room_id).first() is not None


def delete(db: Session, room: Room) -> bool:
    try:
        db.delete(room)
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False
