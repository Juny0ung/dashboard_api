from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from .db import models, schemas, crud
from app.api.dependencies import get_db_session, chk_access

router = APIRouter()


@router.post("/create", tags=["post"])
async def create_dashboard(dashboard: schemas.DashboardCreate, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    if await crud.get_dashboard_by_name(sess = sess, name = dashboard.name):
        raise HTTPException(status_code=400, detail="Already Existed Name")
    return await crud.create_dashboard(sess = sess, dashboard = dashboard, creator = user_id)

@router.put("/update", tags=["put"])
async def update_dashboard(dashboard: schemas.DashboardCreate, id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    update_dash = await crud.update_dashboard(sess = sess, dash_id = id, dashboard = dashboard, user_id = user_id)
    if update_dash:
        return update_dash
    raise HTTPException(status_code=400, detail="Already Existed Name")

@router.post("/delete", tags=["post"])
async def delete_dashboard(id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    if not await crud.delete_dashboard(sess = sess, dash_id = id, user_id = user_id):
        raise HTTPException(status_code=400, detail="Not your dashboard")

@router.get("/get", tags=["get"])
async def get_dashboard(id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    dash = await crud.get_dashboard(sess = sess, dash_id = id, user_id = user_id)
    if dash:
        return dash
    return HTTPException(status_code=400, detail="Cannot Get")

@router.get("/list", tags=["get"])
async def list_dashboard(cursor: schemas.Cursor = schemas.Cursor(), pgsize: int = 10, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    return await crud.list_dashboard(sess = sess, user_id = user_id, cursor = cursor, pgsize = pgsize)