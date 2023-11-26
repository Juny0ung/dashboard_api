from typing import Annotated
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import schemas
from ..db.function import func_post
from ..db.base import get_db_session
from ..token import chk_access

router = APIRouter(
    tags = ["post"]
)


@router.post("", status_code = 201, response_model = schemas.Post)
async def create_post(dashid: int, post: schemas.PostCreate, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = await chk_access(access_token)
    return await func_post.create_post(sess = sess, post = post, user_id = user_id, dash_id=dashid)

@router.put("", status_code = 201, response_model = schemas.Post)
async def update_post(id: int, post: schemas.PostCreate, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = await chk_access(access_token)
    return await func_post.update_post(sess = sess, post_id = id, post = post, user_id = user_id)

@router.delete("", status_code = 200, response_model = schemas.Post)
async def delete_post(id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = await chk_access(access_token)
    return await func_post.delete_post(sess = sess, post_id = id, user_id = user_id)

@router.get("", status_code = 200, response_model = schemas.Post)
async def get_post(id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = await chk_access(access_token)
    return await func_post.get_post(sess = sess, post_id = id, user_id = user_id)

@router.get("/list", status_code = 200, response_model = schemas.PostList)
async def list_post(dashid: int, cursor: str = "0", pgsize: int = 10, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = await chk_access(access_token)
    return await func_post.list_post(sess = sess, dash_id = dashid, user_id = user_id, cursor = cursor, pgsize = pgsize)