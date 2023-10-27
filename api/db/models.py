from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    fullname = Column(String, index = True)
    email = Column(String, unique = True, index = True)
    password = Column(String)
    access_token = Column(String)

    dashboards = relationship("Dashboard", back_populates = "creator")
    posts = relationship("Post", back_populates = "writer")

class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, unique = True, index = True)
    public = Column(Boolean)

    creator = relationship("User", back_populates = "dashboards")
    posts = relationship("Post", back_populates = "dashboard")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String)
    content = Column(String)

    writer = relationship("User", back_populates = "posts")
    dashboard = relationship("Post", back_populates = "posts")