from datetime import datetime
from pyexpat import model
import random
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from app.authentication.oauth2 import create_access_token, make_refresh_record
from app.database import models
from app.database.database import get_db
from app.utils import verify_password, verify_token
from app.schemas import tokens_schemas


router = APIRouter(
    tags=["login"]
)

@router.post("/login", status_code=status.HTTP_200_OK, response_model=tokens_schemas.TokenOut)
def login(login_credentials:OAuth2PasswordRequestForm=Depends(), db:Session=Depends(get_db)):

    query= db.query(models.Users).filter(models.Users.email==login_credentials.username)
    user= query.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user does not exist!")
    
    if not verify_password(login_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token({"user_id": str(user.id), "role":user.role})
    refresh_token = make_refresh_record(db=db, user_id=user.id, days=7)

    return {"access_token":access_token,
            "token_type":"bearer",
            "refresh_token":refresh_token}



@router.post("/token/refresh_token", status_code=status.HTTP_201_CREATED, response_model=tokens_schemas.TokenOut)
def refresh_token(request: tokens_schemas.RefreshRequest, db:Session=Depends(get_db)):

    refresh_tokens=db.query(models.RefreshTokens).filter(models.RefreshTokens.expires_at> datetime.utcnow()).all()
    db_token = None
    
    for token in refresh_tokens:
        if verify_token(request.refresh_token, token.hashed_token):
            db_token=token
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    user_id = db_token.user_id

    # rotate the refresh token
    db.delete(db_token)
    db.commit()

    new_refresh_token= make_refresh_record(db, user_id=user_id)
    new_access_token = create_access_token({"user_id":user_id})

    return {"access_token":new_access_token,
            "token_type":"bearer",
            "refresh_token":new_refresh_token}


