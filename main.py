from fastapi import FastAPI
from database import Base, engine
from routers import auth, task

Base.metadata.create_all(bind=engine)
app= FastAPI(title="FastAPI Task Management API")

app.include_router(auth.router)
app.include_router(task.router)

@app.get("/")
def root():
    return {"message": "FastAPI + PostgreSQL Project Running"}