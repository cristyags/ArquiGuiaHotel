from sqlalchemy.orm import Session

from app.repositories import guest_repo
from app.schemas.guest import GuestCreate


def get_guests(db: Session):
    return guest_repo.get_all(db)


def get_guest(db: Session, guest_id: int):
    return guest_repo.get_by_id(db, guest_id)


def add_guest(db: Session, data: GuestCreate):
    existing = guest_repo.get_by_email(db, data.email)
    if existing:
        return None
    return guest_repo.create(db, data.model_dump())
