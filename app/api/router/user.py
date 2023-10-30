from typing import Annotated
import re
from fastapi import APIRouter, Depends, HTTPException, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import schemas
from ..db.function import func_user
from ..db.base import get_db_session
from app.api.token import set_access_token, delete_access_token

router = APIRouter(
    tags=["user"]
)


@router.post("/login", status_code=204)
async def log_in(user: schemas.UserLogin, res: Response, sess: AsyncSession = Depends(get_db_session)):
    user_id = await func_user.auth_user(sess = sess, user = user)
    res.headers['access-token'] = await set_access_token(user_id)
    return
    

@router.post("/logout", status_code=200)
async def log_out(access_token: Annotated[str | None, Header()] = None):
    user_id = await delete_access_token(access_token)
    return {"id": user_id}

@router.post("", status_code=201, response_model = schemas.UserInfo)
async def create_user(user: schemas.UserCreate, sess: AsyncSession = Depends(get_db_session)):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not re.fullmatch(regex, user.email):
        raise HTTPException(status_code=400, detail="Invalid Email")
    if await func_user.get_user_by_email(sess = sess, email = user.email):
        raise HTTPException(status_code=400, detail="Already Existed Email")
    return await func_user.create_user(sess = sess, user = user)

