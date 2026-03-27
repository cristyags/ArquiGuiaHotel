from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import user_repo
from app.services.auth_service import decode_token


bearer_scheme = HTTPBearer()


def get_current_user(creds=Depends(bearer_scheme), db: Session = Depends(get_db)):
    try:
        token_data = decode_token(creds.credentials)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    if token_data.user_id is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = user_repo.get_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user
