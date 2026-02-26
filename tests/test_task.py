import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from deps import get_db
from database import Base
from routers.task import login_user

DATABASE_URL = "sqlite:///./test_db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_login():
    return 1

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[login_user] = override_login

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_create_task():
    res = client.post("/tasks/", json={"title": "Task1"})
    assert res.status_code == 200
    assert res.json()["title"] == "Task1"

def test_get_tasks():
    client.post("/tasks/", json={"title": "Task1"})
    res = client.get("/tasks/")
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_update_task():
    create = client.post("/tasks/", json={"title": "Old"})
    task_id = create.json()["id"]

    res = client.put(f"/tasks/{task_id}", json={"title": "New"})
    assert res.status_code == 200
    assert res.json()["title"] == "New"

def test_update_not_found():
    res = client.put("/tasks/999", json={"title": "No"})
    assert res.status_code == 404

def test_delete_task():
    create = client.post("/tasks/", json={"title": "Delete"})
    task_id = create.json()["id"]

    res = client.delete(f"/tasks/{task_id}")
    assert res.status_code == 200
    assert res.json()["message"] == "Task deleted successfully"

def test_delete_not_found():
    res = client.delete("/tasks/999")
    assert res.status_code == 404