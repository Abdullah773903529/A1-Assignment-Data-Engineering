from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    pass
class UserUpdate(UserBase):
   pass
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True