from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from .db import models, schemas, crud
from app.api.dependencies import get_db, chk_access

router = APIRouter()


@router.post("/create", tags=["post"])
def create_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    db_post = crud.create_post(db = db, post = post, user_id = user_id, dash_id=id)
    if db_post:
        return db_post
    raise HTTPException(status_code=400, detail="Invalid dashboard")

@router.put("/update", tags=["put"])
def update_post(post: schemas.PostCreate, id: int, db: Session = Depends(get_db), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    update_post = crud.update_post(db = db, post_id = id, post = post, user_id = user_id)
    if update_post:
        return update_post
    raise HTTPException(status_code=400, detail="Already Existed Name")

@router.post("/delete", tags=["post"])
def delete_post(id: int, db: Session = Depends(get_db), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    if not crud.delete_post(db = db, post_id = id, user_id = user_id):
        raise HTTPException(status_code=400, detail="Not your post")

@router.get("/get", tags=["get"])
def get_post(id: int, db: Session = Depends(get_db), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    post = crud.get_post(db = db, post_id = id, user_id = user_id)
    if post:
        return post
    raise HTTPException(status_code=400, detail="Fail")

@router.get("/list", tags=["get"])
def list_post(id: int, cursor: schemas.Cursor = schemas.Cursor(), pgsize: int = 10, db: Session = Depends(get_db), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    posts = crud.list_post(db = db, dash_id = id, user_id = user_id, cursor = cursor, pgsize = pgsize)
    if posts:
        return posts
    raise HTTPException(status_code=400, detail="Fail")