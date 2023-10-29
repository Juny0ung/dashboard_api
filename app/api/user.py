from typing import Annotated
import re
from fastapi import APIRouter, Depends, HTTPException, Header, Response
from sqlalchemy.orm import Session
from app.api.dependencies import set_access_token, delete_access_token, get_db

from .db import schemas, crud


router = APIRouter(
    tags=["user"]
)


@router.post("/login", tags=["post"])
async def log_in(user: schemas.UserLogin, res: Response, db: Session = Depends(get_db)):
    user_id =  crud.auth_user(db, user)
    if user_id:
        res.headers['access-token'] = set_access_token(user_id)
        return
    raise HTTPException(status_code=400, detail="Wrong Information")
    

@router.post("/logout", tags=["post"])
async def log_out(access_token: Annotated[str | None, Header()] = None):
    delete_access_token(access_token)

@router.post("/signup", tags=["post"])
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not re.fullmatch(regex, user.email):
        raise HTTPException(status_code=400, detail="Invalid Email")
    if crud.get_user_by_email(db = db, email = user.email):
        raise HTTPException(status_code=400, detail="Already Existed Email")
    return crud.create_user(db = db, user = user)


