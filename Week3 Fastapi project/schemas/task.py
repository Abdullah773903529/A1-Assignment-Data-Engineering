from pydantic import BaseModel
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = None


class TaskCreate(TaskBase):
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    project_id: int
    assigned_to: Optional[int] = None

    class Config:
        from_attributes = True

class TaskDetail(TaskResponse):
    project: Optional["ProjectResponse"] = None
    assigned: Optional["UserResponse"] = None

from schemas.project import ProjectResponse
from schemas.user import UserResponse
TaskDetail.model_rebuild()