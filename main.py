from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models, schemas, crud
from database import engine, SessionLocal
from auth import create_token, verify_token
from cache import get_cache, set_cache
from crud import create_user , get_user_by_username, authenticate_user

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management API")

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r") as f:
        return f.read()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

        
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
        existing_user = get_user_by_username(db, user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        create_user(db, user)
        return {"message": "User created successfully"}
    

@app.post("/login", response_model=dict)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    user_obj = authenticate_user(db, user.email, user.password)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_token(user_obj.email)
    return {"access_token": access_token, "token_type": "bearer"}

# Create Task
@app.post("/tasks", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, current_user: models.User = Depends(verify_token), db: Session = Depends(get_db)):
    return crud.create_task(db, task, current_user.id)




# Get All Tasks (with caching)
@app.get("/tasks", response_model=list[schemas.TaskOut])
def read_tasks(
    current_user: models.User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    cache_data = get_cache("tasks")

    if cache_data:
        return cache_data

    tasks = crud.get_tasks(db, current_user.id)
    set_cache("tasks", [t.__dict__ for t in tasks])
    return tasks

# Get One Task
@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def read_task(task_id: int, current_user: models.User = Depends(verify_token), db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update Task
@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, task: schemas.TaskUpdate, current_user: models.User = Depends(verify_token), db: Session = Depends(get_db)):
    updated = crud.update_task(db, task_id, task, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

# Delete Task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: models.User = Depends(verify_token), db: Session = Depends(get_db)):
    deleted = crud.delete_task(db, task_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Deleted"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)