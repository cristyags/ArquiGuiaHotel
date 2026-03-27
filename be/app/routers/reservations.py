from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.deps import get_current_user
from app.schemas.reservation import ReservationCreate, ReservationOut, ReservationStatusUpdate, ReservationUpdate
from app.services import reservation_service


router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("/", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
async def create_reservation(data: ReservationCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    reservation, error = reservation_service.create_reservation(db, current_user.id, data)
    if reservation is None:
        raise HTTPException(status_code=422, detail=error or "La habitación no está disponible o el huésped no existe")
    return reservation


@router.get("/mine", response_model=list[ReservationOut])
async def get_my_reservations(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return reservation_service.get_my_reservations(db, current_user.id)


@router.get("/", response_model=list[ReservationOut])
async def get_all_reservations(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return reservation_service.get_all_reservations(db)


@router.get("/{reservation_id}", response_model=ReservationOut)
async def get_reservation(reservation_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    reservation = reservation_service.get_reservation(db, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reservation


@router.patch("/{reservation_id}/status", response_model=ReservationOut)
async def update_reservation_status(reservation_id: int, data: ReservationStatusUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    reservation, error = reservation_service.update_reservation_status(db, reservation_id, current_user.id, data.status)
    if reservation is None:
        code = 404 if error == "Reserva no encontrada" else 422
        raise HTTPException(status_code=code, detail=error or "Transición de estado inválida")
    return reservation


@router.patch("/{reservation_id}", response_model=ReservationOut)
async def update_reservation(reservation_id: int, data: ReservationUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    reservation, error = reservation_service.update_reservation(db, reservation_id, data)
    if reservation is None:
        code = 404 if error in {"Reserva no encontrada", "Habitación no encontrada", "Huésped no encontrado"} else 422
        raise HTTPException(status_code=code, detail=error or "No fue posible actualizar la reserva")
    return reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(reservation_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    deleted, error = reservation_service.delete_reservation(db, reservation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=error or "No fue posible eliminar la reserva")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
