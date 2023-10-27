from pydantic import BaseModel

class PostBase(BaseModel):
    title: str
    content: str
    writer: int
    dashboard: int

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int

    class Config:
        orm_mode = True


class DashboardBase(BaseModel):
    name: str
    public: bool
    creator: str

class DashboardCreate(DashboardBase):
    pass

class Dashboard(DashboardCreate):
    id: int
    posts: list[Post] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    posts: list[Post] = []
    dashboards: list[Dashboard] = []

    class Config:
        orm_mode = True


