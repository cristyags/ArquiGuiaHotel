import asyncio

from fastapi import WebSocket
from sqlalchemy.orm import Session

from app.repositories import notification_repo


_connections: dict[int, WebSocket] = {}


def register_ws(user_id: int, websocket: WebSocket):
    _connections[user_id] = websocket


def unregister_ws(user_id: int):
    _connections.pop(user_id, None)


async def push(user_id: int, payload_dict: dict):
    websocket = _connections.get(user_id)
    if websocket:
        await websocket.send_json(payload_dict)


async def broadcast(payload_dict: dict):
    for websocket in list(_connections.values()):
        try:
            await websocket.send_json(payload_dict)
        except Exception:
            pass


def send(db: Session, user_id: int, title: str, message: str, ntype: str, related_reservation_id: int | None = None):
    notification = notification_repo.create(
        db,
        user_id=user_id,
        title=title,
        message=message,
        ntype=ntype,
        related_reservation_id=related_reservation_id,
    )
    payload = {
        "type": ntype,
        "title": title,
        "message": message,
        "notification_id": notification.id,
        "reservation_id": related_reservation_id,
    }
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(push(user_id, payload))
    except RuntimeError:
        pass
    return notification


def get_user_notifications(db: Session, user_id: int):
    return notification_repo.get_for_user(db, user_id)
