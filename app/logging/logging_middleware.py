
import logging

from httpx import request
from starlette.middleware.base import BaseHTTPMiddleware
from .logging_context import user_id_context
from fastapi import Request
from jose import JWTError,jwt
from app.core.config import settings

logger = logging.getLogger("fintech")
SECRET_KEY =settings.secret_key
ALGORITHM = settings.algorithm


class LoggingMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request:Request, call_next):
        user_id_context.set("-")

# extract jwt token from authorization header of the request
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            if token:
                try:
                    payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
                    user_id = payload.get("user_id")
                    if user_id:
                        user_id_context.set(user_id)
                except JWTError as e:
                    print(f"JWT decode failed: {str(e)}")
        
        try:
            response = await call_next(request)
        finally:
            user_id_context.set("-")
        
        return response 
    