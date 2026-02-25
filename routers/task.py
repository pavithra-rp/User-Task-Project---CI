from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from deps import get_db
from models.task import Task
from schemas.task import TaskCreate, TaskResponse
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM="HS256"

router= APIRouter(prefix="/tasks", tags=["Tasks"])

# Task CRUD Process for Logged in user
def login_user(request: Request):
    token= request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:        
        current_user = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = current_user.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Token is invalid")

        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid")

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session= Depends(get_db), user_id: int= Depends(login_user)):
    new_task= Task(title= task.title, user_id= user_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/")
def get_tasks(db: Session= Depends(get_db)):
    return db.query(Task).all()

@router.put("/{task_id}",response_model=TaskResponse)
def update_task(task_id : int, task_data: TaskCreate, db: Session= Depends(get_db), user_id: int= Depends(login_user)):
    task= db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found.")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    
    task.title = task_data.title
    db.commit()
    db.refresh(task)

    return task

@router.delete("/{task_id}")
def del_task(task_id : int, db: Session= Depends(get_db), user_id: int= Depends(login_user)):
    task= db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found.")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    
    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}