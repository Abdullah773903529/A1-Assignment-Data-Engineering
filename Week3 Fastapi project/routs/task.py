from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.task import Task
from models.project import Project
from models.user import User
from schemas.task import TaskCreate, TaskResponse, TaskDetail

router = APIRouter(prefix="/tasks", tags=["tasks"])



@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):

    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")


    if task.assigned_to is not None:
        user = db.query(User).filter(User.id == task.assigned_to).first()
        if not user:
            raise HTTPException(status_code=404, detail="Assigned user not found")

    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
        task_id: int,
        task_update: TaskCreate,
        db: Session = Depends(get_db)
):

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.project_id != task.project_id:
        project = db.query(Project).filter(Project.id == task_update.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    if task_update.assigned_to != task.assigned_to:
        if task_update.assigned_to is not None:
            user = db.query(User).filter(User.id == task_update.assigned_to).first()
            if not user:
                raise HTTPException(status_code=404, detail="Assigned user not found")

    for key, value in task_update.dict().items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=List[TaskResponse])
def read_tasks(
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[int] = None,
        assigned_to: Optional[int] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Task)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=TaskDetail)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.project_id != task.project_id:
        project = db.query(Project).filter(Project.id == task_update.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="New project not found")

    if task_update.assigned_to != task.assigned_to:
        if task_update.assigned_to is not None:
            user = db.query(User).filter(User.id == task_update.assigned_to).first()
            if not user:
                raise HTTPException(status_code=404, detail="New assigned user not found")

    for key, value in task_update.dict().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None