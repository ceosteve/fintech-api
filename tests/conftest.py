
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


""" test_user fixture"""
@pytest.fixture()
def test_user(client):
    user_info = {
    "first_name": "Steve",
    "last_name": "Njoroge",
    "email": "steve@gmail.com",
    "birthday":"1996-06-10",
    "gender":"M",
    "role":"customer",
    "password": "password233"
    }

    result = client.post("/users/register", json=user_info)
    assert result.status_code == 201

    new_user = result.json()
    new_user['password'] = user_info['password']

    return new_user

