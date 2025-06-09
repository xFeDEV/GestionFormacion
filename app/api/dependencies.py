from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.users import get_user_by_email, get_user_by_id
from core.security import verify_password, verify_token
from core.database import get_db
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/access/token")

def get_current_user(
        token: str = Depends(oauth2_scheme), 
        db: Session = Depends(get_db)
):
    user = verify_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Token Invalido")
    user_db = get_user_by_id(db, user)
    if user_db is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not user_db.estado:
        raise HTTPException(status_code=403, detail="Usuario inactivo. No autorizado")
    return user_db


def authenticate_user(username: str, password: str, db: Session):
    user = get_user_by_email(db, username)
    if not user:
        return False
    if not verify_password(password, user.pass_hash):
        return False
    return user