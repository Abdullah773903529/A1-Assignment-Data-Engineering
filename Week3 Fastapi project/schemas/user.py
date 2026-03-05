from pydantic import BaseModel, EmailStr
from typing import Optional
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    pass
class UserUpdate(UserBase):
   username :  Optional[str] = None
   email: Optional[EmailStr] = None
   is_active: Optional[bool] = True


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True