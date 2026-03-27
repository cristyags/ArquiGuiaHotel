from sqlalchemy.orm import Session

from app.models.guest import Guest


def get_all(db: Session) -> list[Guest]:
    return db.query(Guest).order_by(Guest.full_name.asc()).all()


def get_by_id(db: Session, guest_id: int) -> Guest | None:
    return db.query(Guest).filter(Guest.id == guest_id).first()


def get_by_email(db: Session, email: str) -> Guest | None:
    return db.query(Guest).filter(Guest.email == email).first()


def create(db: Session, data_dict: dict) -> Guest:
    guest = Guest(**data_dict)
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest
