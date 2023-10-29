from typing import Annotated
import re
from fastapi import APIRouter, Depends, HTTPException, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from .db import schemas, crud
from .db.base import get_db_session
from app.api.token import set_access_token, delete_access_token


router = APIRouter(
    tags=["user"]
)


@router.post("/login")
async def log_in(user: schemas.UserLogin, res: Response, sess: AsyncSession = Depends(get_db_session)):
    user_id = await crud.auth_user(sess = sess, user = user)
    if user_id:
        res.headers['access-token'] = set_access_token(user_id)
        return
    raise HTTPException(status_code=400, detail="Wrong Information")
    

@router.post("/logout")
def log_out(access_token: Annotated[str | None, Header()] = None):
    return delete_access_token(access_token)

@router.post("/signup")
async def create_user(user: schemas.UserCreate, sess: AsyncSession = Depends(get_db_session)):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not re.fullmatch(regex, user.email):
        raise HTTPException(status_code=400, detail="Invalid Email")
    if await crud.get_user_by_email(sess = sess, email = user.email):
        raise HTTPException(status_code=400, detail="Already Existed Email")
    return await crud.create_user(sess = sess, user = user)

