from typing import Generator

from pathlib import Path
import pytest
import unittest
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from main import app, get_db
from database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///test_main_db.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db()-> Session:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# client = TestClient(app)

@pytest.fixture(scope="module")
def client():
    test_db = Path("./test_main_db.db")
    if test_db.is_file():  # pragma: nocover
        test_db.unlink()
    from main import app
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    if test_db.is_file():  # pragma: nocover
        test_db.unlink()

def test_create_user(client):
    db = next(override_get_db())
    db.flush()
    response = client.post("/user", json=dict(username="test", password="test"))
    assert response.status_code == 200


def test_login(client):
    db = next(override_get_db())
    db.flush()
    client.post("/user", json=dict(username="test", password="test"))
    response = client.post("/login", json=dict(username="test", password="test"))
    assert response.status_code == 200


def test_get_current_user(client):
    db = next(override_get_db())
    db.flush()
    client.post("/user", json=dict(username="test", password="test"))
    response = client.post("/login", json=dict(username="test", password="test"))
    assert response.status_code == 200
    token = response.json()["access_token"]
    response = client.get("/user/get-current", headers=dict(Authorization=f"Bearer {token}"))
    assert response.status_code == 200
    assert response.json() == {"username":"test", "password":"test", "id":1}


def test_get_users(client):
    db = next(override_get_db())
    db.flush()
    
    client.post("/user", json=dict(username="test", password="test"))
    client.post("/user", json=dict(username="test2", password="test2"))
    client.post("/user", json=dict(username="test3", password="test3"))

    response = client.post("/login", json=dict(username="test", password="test"))
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get("/user", headers=dict(Authorization=f"Bearer {token}"))
    assert response.status_code == 200
    assert response.json() == [
        {"username":"test", "password":"test", "id":1},
        {"username":"test2", "password":"test2", "id":2},
        {"username":"test3", "password":"test3", "id":3},
    ]


if __name__ == "__main__":
    pytest.main()
    # os.remove("./test_main_db.db")