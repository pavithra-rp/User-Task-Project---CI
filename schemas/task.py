from pydantic import BaseModel

class TaskCreate(BaseModel):
    title : str

class TaskResponse(BaseModel):
    id : int
    title : str
    user_id: int
    
    class config:
        orm_mode = True