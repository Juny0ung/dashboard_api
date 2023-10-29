from pydantic import BaseModel

class PostBase(BaseModel):
    title: str
    content: str = ""

class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    writer: int
    dashboard: int

    class Config:
        orm_mode = True


class DashboardBase(BaseModel):
    name: str
    public: bool

class DashboardCreate(DashboardBase):
    pass

class Dashboard(DashboardCreate):
    id: int
    posts_cnt: int
    posts: list[Post] = []
    creator: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str

class UserLogin(UserBase):
    password: str

class UserCreate(UserBase):
    password: str
    fullname: str

class User(UserBase):
    id: int
    posts: list[Post] = []
    dashboards: list[Dashboard] = []

    class Config:
        orm_mode = True


class Cursor(BaseModel):
    is_sort: int = 0            # 0 : with id, 1 : with the number of posts (descending order)

    id: int | None = None
    posts_cnt: int | None = None

