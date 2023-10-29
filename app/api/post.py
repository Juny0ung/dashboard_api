from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from .db import models, schemas, crud
from app.api.dependencies import get_db_session, chk_access

router = APIRouter()


@router.post("/create", tags=["post"])
async def create_post(id: int, post: schemas.PostCreate, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    db_post = await crud.create_post(sess = sess, post = post, user_id = user_id, dash_id=id)
    if db_post:
        return db_post
    raise HTTPException(status_code=400, detail="Invalid dashboard")

@router.put("/update", tags=["put"])
async def update_post(post: schemas.PostCreate, id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    update_post = await crud.update_post(sess = sess, post_id = id, post = post, user_id = user_id)
    if update_post:
        return update_post
    raise HTTPException(status_code=400, detail="Not your post")

@router.post("/delete", tags=["post"])
async def delete_post(id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    if not await crud.delete_post(sess = sess, post_id = id, user_id = user_id):
        raise HTTPException(status_code=400, detail="Not your post")

@router.get("/get", tags=["get"])
async def get_post(id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    post = await crud.get_post(sess = sess, post_id = id, user_id = user_id)
    if post:
        return post
    raise HTTPException(status_code=400, detail="Fail")

@router.get("/list", tags=["get"])
async def list_post(id: int, cursor: schemas.Cursor = schemas.Cursor(), pgsize: int = 10, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    result = await crud.list_post(sess = sess, dash_id = id, user_id = user_id, cursor = cursor, pgsize = pgsize)
    if result:
        return result
    raise HTTPException(status_code=400, detail="Fail")