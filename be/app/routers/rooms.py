from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.deps import get_current_user
from app.schemas.room import RoomCreate, RoomOut, RoomStatusUpdate, RoomUpdate
from app.services import room_service


router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=list[RoomOut])
async def get_rooms(db: Session = Depends(get_db)):
    return room_service.get_rooms(db)


@router.get("/available", response_model=list[RoomOut])
async def get_available_rooms(db: Session = Depends(get_db)):
    return room_service.get_available_rooms(db)


@router.get("/{room_id}", response_model=RoomOut)
async def get_room(room_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rooms = room_service.get_rooms(db)
    room = next((item for item in rooms if item.id == room_id), None)
    if room is None:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    return room


@router.post("/", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
async def add_room(data: RoomCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    room, error = room_service.add_room(db, data)
    if room is None:
        raise HTTPException(status_code=422, detail=error or "Datos de habitación inválidos")
    return room


@router.patch("/{room_id}", response_model=RoomOut)
async def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    room, error = room_service.update_room(db, room_id, data)
    if room is None:
        code = 404 if error == "Habitación no encontrada" else 422
        raise HTTPException(status_code=code, detail=error or "No fue posible actualizar la habitación")
    return room


@router.patch("/{room_id}/status", response_model=RoomOut)
async def update_room_status(room_id: int, payload: RoomStatusUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    room, error = room_service.update_room_status(db, room_id, payload.status)
    if room is None:
        code = 404 if error == "Habitación no encontrada" else 422
        raise HTTPException(status_code=code, detail=error or "Valor de estado inválido")
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    deleted, error = room_service.delete_room(db, room_id)
    if not deleted:
        code = 404 if error == "Habitación no encontrada" else 422
        raise HTTPException(status_code=code, detail=error or "No fue posible eliminar la habitación")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
