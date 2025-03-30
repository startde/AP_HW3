from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None

class LinkCreate(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkInfo(BaseModel): 
    short_code:str
    original_url:HttpUrl
    created_at: datetime
    expires_at: datetime | None  

class UserInfo(BaseModel):
    id: int
    username: str
    email: EmailStr | None
    created_at: datetime