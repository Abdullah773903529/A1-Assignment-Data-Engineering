from pydantic import BaseModel
from typing import Optional

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    owner_id: int

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class ProjectWithOwner(ProjectResponse):
    owner: Optional["UserResponse"] = None

from schemas.user import UserResponse
ProjectWithOwner.model_rebuild()