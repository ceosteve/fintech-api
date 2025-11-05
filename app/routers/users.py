
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import models
from app.database.database import get_db
from app.schemas import users_schemas
from app import utils

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=users_schemas.UserOut)
def create_account(user_data:users_schemas.UserCreate, db:Session=Depends(get_db)):

    existing_user = db.query(models.Users).filter(models.Users.email==user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"user with {user_data.email} already exists")
    
    hashed_password = utils.hash_password(user_data.password)
    user_data.password = hashed_password

    new_user = models.Users(**user_data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=users_schemas.UserResponse)
def get_user(id:str, db:Session=Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.public_id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with {id} not found")
    
    return user


