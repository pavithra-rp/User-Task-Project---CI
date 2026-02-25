import pytest
from fastapi.testclient import TestClient
from models.user import User, Base
from deps import get_db
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# test DB 
DATABASE_URL="sqlite:///./test_db"  # Sqlite for testing
engine= create_engine(DATABASE_URL, connect_args={"check_same_thread":False})
TestingSessionlocal= sessionmaker(bind=engine, autocommit=False, autoflush=False)

# to use test db
def override_get_db():
    db= TestingSessionlocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db]=override_get_db

# create table before tests
Base.metadata.create_all(bind=engine)

# initialize test client
client= TestClient(app)

# @pytest.fixture(autouse=True)
# def reset_db():
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
    
# new user
def test_register_user():
    response= client.post("/auth/register", json={"username":"testuser","password":"secret"})
    assert response.status_code == 200
    assert response.json()["message"] == "User added successfully.."

# existing user
def test_register_exiting_user():
    client.post("/auth/register", json={"username":"testuser","password":"secret"})
    response = client.post("/auth/register", json={"username":"testuser","password":"secret"})
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

# login user
def test_login_user():
    response= client.post("auth/login",json={"username":"testuser","password":"secret"})
    assert response.status_code == 200
    assert response.json()["message"] == "Login Success"
    assert "access_token" in response.cookies

# Login with wrong password
def test_login_invalid_user():
    response = client.post("/auth/login", json={"username": "alice", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Credentials"

# Logout should remove cookie
def test_logout_user():
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out"

def test_forgot_password():
    # create user first
    client.post("/auth/register", json={"username": "alice", "password": "123456"})
    response = client.post("/auth/forgot-password", json={"username": "alice"})
    assert response.status_code == 200
    json_data = response.json()
    assert "reset_token" in json_data
    assert json_data["message"] == "token to reset password"

def test_reset_password():
    # create user
    client.post("/auth/register", json={"username": "alice", "password": "123456"})
    # First, get reset token
    response = client.post("/auth/forgot-password", json={"username": "alice"})
    token = response.json()["reset_token"]

    # Reset password using token
    response = client.post("/auth/reset-password", json={ "token": token, "new_password": "newsecret"})
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successful..."