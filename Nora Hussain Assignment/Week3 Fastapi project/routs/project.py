from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.project import Project
from models.user import User
from schemas.project import ProjectCreate, ProjectResponse, ProjectWithOwner, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == project.owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Owner not found")

    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")


    if project_update.owner_id is not None:
        user = db.query(User).filter(User.id == project_update.owner_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Owner not found")

    update_data = project_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/", response_model=List[ProjectResponse])
def read_projects(skip: int = 0, limit: int = 100, owner_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Project)
    if owner_id:
        query = query.filter(Project.owner_id == owner_id)
    projects = query.offset(skip).limit(limit).all()
    return projects


# قراءة مشروع معين مع تفاصيل المالك
@router.get("/{project_id}", response_model=ProjectWithOwner)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# تحديث مشروع
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_update: ProjectCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # التحقق من وجود المالك الجديد إذا تغير
    if project_update.owner_id != project.owner_id:
        user = db.query(User).filter(User.id == project_update.owner_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="New owner not found")

    for key, value in project_update.dict().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


# حذف مشروع
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return None