from sqlalchemy.orm import Session
from api.db import crud, models, schemas
from api.db.base import SessionLocal, engine

models.Base.metadata.create_all(bind = engine)

from fastapi import FastAPI

from api import user, post, dashboard

app = FastAPI()

app.include_router(User.router, prefix='/account')
app.include_router(dashboard.router, prefix='/dashboard')
app.include_router(post.router, prefix='/post')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


