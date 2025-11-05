
from datetime import date
from uuid import UUID
from pydantic import BaseModel, EmailStr
import shortuuid
from app.database.models import Gender


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    birthday: date
    gender: Gender
    role: str
    password: str

class UserOut(BaseModel):
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    first_name:str
    last_name: str
    email:EmailStr
    public_id:str

