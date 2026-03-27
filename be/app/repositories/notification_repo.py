from sqlalchemy.orm import Session

from app.models.notification import Notification


def create(db: Session, user_id: int, title: str, message: str, ntype: str, related_reservation_id: int | None = None) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=ntype,
        related_reservation_id=related_reservation_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_for_user(db: Session, user_id: int) -> list[Notification]:
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()


def mark_read(db: Session, notification_id: int, user_id: int) -> Notification | None:
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if not notification:
        return None
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
