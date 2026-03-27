from sqlalchemy.orm import Session

from app.repositories import room_repo
from app.schemas.room import RoomCreate, RoomUpdate


VALID_ROOM_TYPES = {"single", "double", "suite", "family"}
VALID_ROOM_STATUS = {"available", "occupied", "cleaning", "maintenance"}


def get_rooms(db: Session):
    return room_repo.get_all(db)


def get_available_rooms(db: Session):
    return room_repo.get_available(db)


def add_room(db: Session, data: RoomCreate):
    if data.room_type not in VALID_ROOM_TYPES or data.status not in VALID_ROOM_STATUS:
        return None, "Datos de habitación inválidos"
    room = room_repo.create(db, data.model_dump())
    if room is None:
        return None, "Ya existe una habitación con ese número"
    return room, None


def update_room(db: Session, room_id: int, data: RoomUpdate):
    room = room_repo.get_by_id(db, room_id)
    if not room:
        return None, "Habitación no encontrada"
    values = data.model_dump(exclude_unset=True)
    if "room_type" in values and values["room_type"] not in VALID_ROOM_TYPES:
        return None, "Tipo de habitación inválido"
    if "status" in values and values["status"] not in VALID_ROOM_STATUS:
        return None, "Estado de habitación inválido"
    updated = room_repo.update(db, room, values)
    if updated is None:
        return None, "No fue posible actualizar la habitación"
    return updated, None


def update_room_status(db: Session, room_id: int, new_status: str):
    if new_status not in VALID_ROOM_STATUS:
        return None, "Valor de estado inválido"
    room = room_repo.get_by_id(db, room_id)
    if not room:
        return None, "Habitación no encontrada"
    return room_repo.update_status(db, room, new_status), None


def delete_room(db: Session, room_id: int):
    room = room_repo.get_by_id(db, room_id)
    if not room:
        return False, "Habitación no encontrada"
    if room_repo.has_reservations(db, room_id):
        return False, "No se puede eliminar una habitación con reservas asociadas"
    deleted = room_repo.delete(db, room)
    if not deleted:
        return False, "No fue posible eliminar la habitación"
    return True, None
