from pydantic import BaseModel
from typing import List

class PostBase(BaseModel):
    title: str
    content: str = ""

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    writer_id: int
    dashboard_id: int

    class Config:
        orm_mode = True

class PostList(BaseModel):
    results: List[Post]
    next_cursor: str
    current_cursor: str



class DashboardBase(BaseModel):
    name: str
    public: bool

class DashboardCreate(DashboardBase):
    pass

class DashboardInfo(DashboardBase):
    id: int
    creator_id: int
    posts_cnt: int
    class Config:
        orm_mode = True

class Dashboard(DashboardInfo):
    posts: list[Post] = []
    class Config:
        orm_mode = True

class DashboardList(BaseModel):
    results: List[DashboardInfo]
    next_cursor: str
    current_cursor: str

class UserBase(BaseModel):
    email: str

class UserLogin(UserBase):
    password: str

class UserCreate(UserBase):
    password: str
    fullname: str

class UserInfo(UserBase):
    id: int
    fullname: str

class User(UserInfo):
    posts: list[Post] = []
    dashboards: list[Dashboard] = []

    class Config:
        orm_mode = True

