import smtplib
from email.mime.text import MIMEText
import token

from passlib.context import CryptContext

password_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password:str) -> str:
    return password_context.hash(password)

def verify_password(raw_password, hashed_password)-> bool:
    return password_context.verify(raw_password,hashed_password)

def hash_token(token:str)->str:
    return password_context.hash(token)

def verify_token(raw_token:str, hashed_token:str) -> bool:
    return password_context.verify(raw_token,hashed_token)
