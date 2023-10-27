from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from access_token import get_user_id

from .db import models, schemas, crud

# Dependency
from .db.base import SessionLocal
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.get("/", tags=["get"])
def first_get():
    return {"message": "Hello World"}


@router.post("/create", tags=["post"])
def create_post(dash_id: int, post: schemas.PostCreate, token: str, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Access")
    if crud.is_valid_dash(db = db, dash_id = dash_id, user_id = user_id):
        return crud.create_post(db = db, post = post, user_id = user_id, dash_id=dash_id)
    raise HTTPException(status_code = 400, detail = "Invalid Dashboard")

@router.put("/update", tags=["put"])
def update_post(post_id: int, title: str, content: str, token: str, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Access")
    update_post = crud.update_post(db = db, post_id = post_id, title = title, content = content, usr_id = user_id)
    if update_post:
        return update_post
    raise HTTPException(status_code=400, detail="Already Existed Name")

@router.post("/delete", tags=["post"])
def delete_post(post_id: int, token: str, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Access")
    return crud.delete_post(db = db, post_id = post_id, user_id = user_id)

@router.get("/get", tags=["get"])
def get_post(post_id: int, token: str, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Access")
    post = crud.get_post(db = db, post_id = post_id, user_id = user_id)
    if post:
        return post
    return HTTPException(status_code=400, detail="Fail")

@router.get("/list", tags=["get"])
def list_post(token: str, dash_id: int, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Access")
    return crud.list_post(db = db, dash_id = dash_id, user_id = user_id)