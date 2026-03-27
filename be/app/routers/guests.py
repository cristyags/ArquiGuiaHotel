from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.deps import get_current_user
from app.schemas.guest import GuestCreate, GuestOut
from app.services import guest_service


router = APIRouter(prefix="/guests", tags=["guests"])


@router.get("/", response_model=list[GuestOut])
async def get_guests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return guest_service.get_guests(db)


@router.get("/{guest_id}", response_model=GuestOut)
async def get_guest(guest_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    guest = guest_service.get_guest(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Huésped no encontrado")
    return guest


@router.post("/", response_model=GuestOut, status_code=status.HTTP_201_CREATED)
async def add_guest(data: GuestCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    guest = guest_service.add_guest(db, data)
    if guest is None:
        raise HTTPException(status_code=409, detail="Ya existe un huésped con ese correo")
    return guest
