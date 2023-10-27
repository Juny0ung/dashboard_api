from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from access_token import set_access_token, delete_access_token

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


@router.post("/login", tags=["post"])
def log_in(user_id: str, password: str):
    # TODO: authentication
    isauth = True
    if isauth:
        # TODO: Generate token
        token = "12345"
        set_access_token(user_id, token)
        return {"token" : token}
    return {"error": "Invalid Information"}

@router.post("/logout", tags=["post"])
def log_out(user_id: str):
    delete_access_token(user_id)

@router.post("/signup", tags=["post"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db = db, email = user.email):
        raise HTTPException(status_code=400, detail="Already Existed Email")
    return crud.create_user(db = db, user = user)


