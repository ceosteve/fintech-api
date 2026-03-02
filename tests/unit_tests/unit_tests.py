from jose import jwt
from app.core.config import settings
from app.authentication.oauth2 import create_access_token
from app.utils import hash_password, hash_token, verify_password


def test_hash_password():
    password = 'steven01njoro'

    hashed_password = hash_password(password)

    assert isinstance(hashed_password, str)
    assert hashed_password.startswith("$argon")

    assert verify_password(password, hashed_password)



def test_hash_acccess_tokens():

    access_token = create_access_token({"user_id":22, "role":"customer"})

    hashed_token = hash_token(access_token)

    assert isinstance(hashed_token, str)
    assert access_token != hashed_token
