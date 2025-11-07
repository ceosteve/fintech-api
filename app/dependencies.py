
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.authentication.oauth2 import verify_access_token
from app.database import models
from app.database.database import get_db
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer("login")


def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    credentials_exception= HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="could not verify credentials", 
                                         headers={"WWW-Authentication":"Bearer"})
    
    token_data = verify_access_token(token, credentials_exception)

    user = db.query(models.Users).filter(models.Users.id==token_data.id).first()
    if not user:
        raise credentials_exception
    return user
