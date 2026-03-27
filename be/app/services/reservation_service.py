from sqlalchemy.orm import Session

from app.repositories import guest_repo, reservation_repo, room_repo
from app.services import notification_service


ACTIVE_ROOM_STATUSES = {"confirmed", "checked_in"}


def create_reservation(db: Session, staff_id: int, data):
    if data.check_out_date <= data.check_in_date:
        return None, "La fecha de salida debe ser posterior a la fecha de ingreso"
    room = room_repo.get_by_id(db, data.room_id)
    if not room or room.status != "available":
        return None, "La habitación no está disponible"
    guest = guest_repo.get_by_id(db, data.guest_id)
    if not guest:
        return None, "El huésped no existe"
    reservation = reservation_repo.create(
        db,
        room_id=room.id,
        guest_id=guest.id,
        staff_id=staff_id,
        check_in_date=data.check_in_date,
        check_out_date=data.check_out_date,
        nightly_rate=float(room.price_per_night),
        notes=data.notes,
    )
    room_repo.update_status(db, room, "occupied")
    notification_service.send(
        db,
        user_id=staff_id,
        title="Reserva creada",
        message=f"La reserva para la habitación {room.room_number} fue creada correctamente.",
        ntype="reservation_created",
        related_reservation_id=reservation.id,
    )
    return reservation, None


def get_my_reservations(db: Session, staff_id: int):
    return reservation_repo.get_by_staff(db, staff_id)


def get_all_reservations(db: Session):
    return reservation_repo.get_all(db)


def get_reservation(db: Session, reservation_id: int):
    return reservation_repo.get_by_id(db, reservation_id)


def update_reservation_status(db: Session, reservation_id: int, requesting_user_id: int, new_status: str):
    reservation = reservation_repo.get_by_id(db, reservation_id)
    if not reservation:
        return None, "Reserva no encontrada"
    valid_transitions = {
        "confirmed": {"checked_in", "cancelled"},
        "checked_in": {"checked_out"},
    }
    if new_status not in valid_transitions.get(reservation.status, set()):
        return None, "Transición de estado inválida"
    updated = reservation_repo.update_status(db, reservation, new_status)
    room = room_repo.get_by_id(db, reservation.room_id)
    if not room:
        return None, "Habitación no encontrada"
    if new_status == "checked_in":
        room_repo.update_status(db, room, "occupied")
        notification_service.send(
            db,
            user_id=reservation.staff_id,
            title="Check-in completado",
            message=f"El huésped de la habitación {room.room_number} ya hizo check-in.",
            ntype="guest_checked_in",
            related_reservation_id=reservation.id,
        )
    elif new_status == "checked_out":
        room_repo.update_status(db, room, "cleaning")
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            loop.create_task(
                notification_service.broadcast(
                    {
                        "type": "room_status_update",
                        "room_id": room.id,
                        "room_number": room.room_number,
                        "new_status": "cleaning",
                    }
                )
            )
        except RuntimeError:
            pass
        notification_service.send(
            db,
            user_id=reservation.staff_id,
            title="Check-out completado",
            message=f"La habitación {room.room_number} pasó a limpieza.",
            ntype="guest_checked_out",
            related_reservation_id=reservation.id,
        )
    elif new_status == "cancelled":
        room_repo.update_status(db, room, "available")
        notification_service.send(
            db,
            user_id=reservation.staff_id,
            title="Reserva cancelada",
            message=f"La reserva de la habitación {room.room_number} fue cancelada.",
            ntype="reservation_cancelled",
            related_reservation_id=reservation.id,
        )
    return updated, None


def update_reservation(db: Session, reservation_id: int, data):
    reservation = reservation_repo.get_by_id(db, reservation_id)
    if not reservation:
        return None, "Reserva no encontrada"
    if reservation.status in {"checked_out", "cancelled"}:
        return None, "No se puede editar una reserva finalizada o cancelada"
    if data.check_out_date <= data.check_in_date:
        return None, "La fecha de salida debe ser posterior a la fecha de ingreso"
    room = room_repo.get_by_id(db, data.room_id)
    if not room:
        return None, "Habitación no encontrada"
    guest = guest_repo.get_by_id(db, data.guest_id)
    if not guest:
        return None, "Huésped no encontrado"

    previous_room = room_repo.get_by_id(db, reservation.room_id)
    if reservation.room_id != data.room_id:
        if room.status != "available":
            return None, "La nueva habitación no está disponible"
        if previous_room and reservation.status in ACTIVE_ROOM_STATUSES:
            room_repo.update_status(db, previous_room, "available")
        room_repo.update_status(db, room, "occupied")

    updated = reservation_repo.update_reservation(
        db,
        reservation,
        room_id=room.id,
        guest_id=guest.id,
        check_in_date=data.check_in_date,
        check_out_date=data.check_out_date,
        nightly_rate=float(room.price_per_night),
        notes=data.notes,
    )

    notification_service.send(
        db,
        user_id=reservation.staff_id,
        title="Reserva actualizada",
        message=f"La reserva #{reservation.id} fue actualizada correctamente.",
        ntype="general",
        related_reservation_id=reservation.id,
    )
    return updated, None


def delete_reservation(db: Session, reservation_id: int):
    reservation = reservation_repo.get_by_id(db, reservation_id)
    if not reservation:
        return False, "Reserva no encontrada"
    room = room_repo.get_by_id(db, reservation.room_id)
    if room and reservation.status in ACTIVE_ROOM_STATUSES:
        room_repo.update_status(db, room, "available")
    reservation_repo.delete(db, reservation)
    return True, None
