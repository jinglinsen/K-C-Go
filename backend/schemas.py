from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    role: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[str] = None
    category: Optional[str] = "General"

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: int
    user_id: int
    status: str
    view_count: int
    like_count: int
    comment_count: int
    created_at: datetime
    last_activity: datetime
    author: UserOut
    participants: Optional[List[UserOut]] = []

    class Config:
        orm_mode = True
        from_attributes = True

class CommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    pass

class CommentOut(CommentBase):
    id: int
    post_id: int
    user_id: int
    level: int
    created_at: datetime
    author: UserOut
    
    class Config:
        orm_mode = True
        from_attributes = True
