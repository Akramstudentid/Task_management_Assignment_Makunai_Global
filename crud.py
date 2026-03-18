from sqlalchemy.orm import Session
import models, schemas
from auth import hash_password, verify_password

def get_user_by_username(db, username):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db, email):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db, user):
    hashed_password = hash_password(user.password)
    db_user = models.User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_task(db: Session, task: schemas.TaskCreate, owner_id: int):
    db_task = models.Task(**task.dict(), owner_id=owner_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, owner_id: int | None = None):
    query = db.query(models.Task)
    if owner_id is not None:
        query = query.filter(models.Task.owner_id == owner_id)
    return query.all()

def get_task(db: Session, task_id: int, owner_id: int | None = None):
    query = db.query(models.Task).filter(models.Task.id == task_id)
    if owner_id is not None:
        query = query.filter(models.Task.owner_id == owner_id)
    return query.first()

def update_task(db: Session, task_id: int, task: schemas.TaskUpdate, owner_id: int | None = None):
    db_task = get_task(db, task_id, owner_id=owner_id)
    if not db_task:
        return None

    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, owner_id: int | None = None):
    db_task = get_task(db, task_id, owner_id=owner_id)
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task