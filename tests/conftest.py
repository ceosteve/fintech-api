
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app.authentication.oauth2 import create_access_token
from app.main import app
from app.database.database import  get_db, Base
from app.database import models

DATABASE_URL = "postgresql+psycopg2://postgres:postgres254@localhost:5432/fintech_test"

engine = create_engine(DATABASE_URL)

TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)



"""create a new session for each test"""
@pytest.fixture(scope='function')
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestSession()
    try:
        yield db
    finally:
        db.close()


"""create a test client, which will send HTTP requests
   to endpoints without running the entire application server"""

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db]=override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


""" test_user fixture"""
@pytest.fixture()
def test_user(client):
    user_info = {
    "first_name": "Steve",
    "last_name": "Njoroge",
    "email": "steve@gmail.com",
    "birthday":"1996-06-10",
    "gender":"Male",
    "role":"customer",
    "password": "password233"
    }

    result = client.post("/users/register", json=user_info)
    assert result.status_code == 201

    new_user = result.json()
    new_user['password'] = user_info['password']

    return new_user


"""create access token fixture"""
@pytest.fixture()
def customer_token(test_user):
    return create_access_token(data = {"user_id": test_user['id']})


@pytest.fixture
def authorised_client(client, customer_token):
    new_client = client.__class__(app=client.app, base_url=client.base_url)
    new_client.headers={
        **client.headers, 
        'Authorization':f"Bearer {customer_token}"
    }

    return new_client


