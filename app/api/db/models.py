from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, nullable = False)
    fullname = Column(String, nullable = False)
    email = Column(String, unique = True, index = True, nullable = False)
    hash_password = Column(String, nullable = False)
    salt = Column(String, nullable = False)

    dashboards = relationship("Dashboard", back_populates = "creator", cascade='all, delete-orphan')
    posts = relationship("Post", back_populates = "writer", cascade='all, delete-orphan')

class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key = True, index = True, nullable = False)
    name = Column(String, unique = True, index = True, nullable = False)
    public = Column(Boolean, default = True, nullable = False)
    posts_cnt = Column(Integer, index = True, nullable = False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable = False)

    creator = relationship("User", back_populates = "dashboards")
    posts = relationship("Post", back_populates = "dashboard", cascade='all, delete-orphan')

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key = True, index = True, nullable = False)
    title = Column(String, nullable = False)
    content = Column(String)
    writer_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), index = True, nullable = False)

    writer = relationship("User", back_populates = "posts")
    dashboard = relationship("Dashboard", back_populates = "posts")