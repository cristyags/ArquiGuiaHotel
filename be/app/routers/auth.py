from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import user_repo
from app.schemas.token import Token
from app.schemas.user import LoginRequest, UserCreate, UserOut
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    if user_repo.get_by_username(db, data.username):
        raise HTTPException(status_code=409, detail="El nombre de usuario ya existe")
    if user_repo.get_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="El correo ya existe")
    created = auth_service.register(db, data)
    return created


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    token = auth_service.login(db, data.username, data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return Token(access_token=token)
