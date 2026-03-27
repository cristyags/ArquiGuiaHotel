from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.reservation import Reservation


def create(db: Session, room_id: int, guest_id: int, staff_id: int, check_in_date: date, check_out_date: date, nightly_rate: float, notes: str | None) -> Reservation:
    days = (check_out_date - check_in_date).days
    total_amount = Decimal(str(nightly_rate)) * Decimal(days)
    reservation = Reservation(
        room_id=room_id,
        guest_id=guest_id,
        staff_id=staff_id,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        nightly_rate=nightly_rate,
        total_amount=total_amount,
        status="confirmed",
        notes=notes,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def get_by_staff(db: Session, staff_id: int) -> list[Reservation]:
    return db.query(Reservation).filter(Reservation.staff_id == staff_id).order_by(Reservation.created_at.desc()).all()


def get_all(db: Session) -> list[Reservation]:
    return db.query(Reservation).order_by(Reservation.created_at.desc()).all()


def get_by_id(db: Session, reservation_id: int) -> Reservation | None:
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()


def update_status(db: Session, reservation: Reservation, new_status: str) -> Reservation:
    reservation.status = new_status
    db.commit()
    db.refresh(reservation)
    return reservation


def update_reservation(
    db: Session,
    reservation: Reservation,
    room_id: int,
    guest_id: int,
    check_in_date: date,
    check_out_date: date,
    nightly_rate: float,
    notes: str | None,
) -> Reservation:
    days = (check_out_date - check_in_date).days
    reservation.room_id = room_id
    reservation.guest_id = guest_id
    reservation.check_in_date = check_in_date
    reservation.check_out_date = check_out_date
    reservation.nightly_rate = nightly_rate
    reservation.total_amount = Decimal(str(nightly_rate)) * Decimal(days)
    reservation.notes = notes
    db.commit()
    db.refresh(reservation)
    return reservation


def delete(db: Session, reservation: Reservation) -> None:
    db.delete(reservation)
    db.commit()
