from pydantic import BaseModel

class UserCreate(BaseModel):
    
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    email: str
    password: str

class TaskCreate(BaseModel):
    title: str
    description: str

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    owner_id: int

    class Config:
        orm_mode = True