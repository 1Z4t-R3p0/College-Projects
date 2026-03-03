from pydantic import BaseModel
import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TicketBase(BaseModel):
    title: str
    description: str

class TicketCreate(TicketBase):
    pass

class TicketResponse(TicketBase):
    id: int
    category: str
    created_at: datetime.datetime
    user_id: int | None

    class Config:
        from_attributes = True
