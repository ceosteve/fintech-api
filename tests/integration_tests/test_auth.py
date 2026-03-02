
from jose import jwt
from app.schemas import tokens_schemas
from app.core.config import settings



"""create a test for user login into the system"""

def test_user_login(client, test_user):
    result=client.post("/login", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })

    login_data = tokens_schemas.TokenOut(**result.json())
    payload = jwt.decode(login_data.access_token, settings.secret_key, settings.algorithm)
    user_id = payload["user_id"]
    assert user_id == test_user['id']
    assert login_data.token_type == "bearer"
    assert result.status_code == 200


"""test incorrect login"""
def test_incorrect_login(client, test_user):
    result = client.post("/login", data={
        "username": test_user["email"],
        "password": 'password234'
    })

    assert result.status_code == 404
    assert result.json().get('detail') == 'Invalid Password!'