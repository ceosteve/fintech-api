from datetime import datetime, timedelta, timezone
import secrets
from app.database import models
from app.database.database import get_db
from app.utils import hash_token
from app.core.config import settings
from jose import JWTError, jwt
from app.schemas import tokens_schemas
from sqlalchemy.orm import Session
from fastapi import Depends

ALGORITHM= settings.algorithm
EXPIRATION_TIME= settings.access_token_expiration_time
SECRET_KEY = settings.secret_key


def create_access_token(data:dict):
    to_encode= data.copy()
    expires = datetime.utcnow() + timedelta(minutes=EXPIRATION_TIME)
    to_encode.update({"exp":expires})

    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token:str, credentials_exception):
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id:str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        
        token_data= tokens_schemas.TokenData(id=id)
        return token_data
    except JWTError:
        credentials_exception

def generate_raw_refresh_token() -> str:
    return secrets.token_urlsafe(64)


''''make a new record of refresh token in the database'''
def make_refresh_record(user_id:str, db:Session=Depends(get_db), days:int=settings.refresh_token_expiration_days):
    raw_token=generate_raw_refresh_token()
    hashed_token=hash_token(raw_token)
    expires_at = datetime.utcnow() + timedelta(days=days)
    db_token = models.RefreshTokens(user_id=user_id, expires_at=expires_at, hashed_token=hashed_token)

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return raw_token

    

