from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import schemas
from ..db.function import func_dash
from ..db.base import get_db_session
from ..token import chk_access

router = APIRouter(
    tags = ["dashboard"]
)


@router.post("/create")
async def create_dashboard(dashboard: schemas.DashboardCreate, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = await chk_access(access_token)
    if await func_dash.get_dashboard_by_name(sess = sess, name = dashboard.name):
        raise HTTPException(status_code=400, detail="Already Existed Name")
    return await func_dash.create_dashboard(sess = sess, dashboard = dashboard, creator = user_id)

@router.put("/update")
async def update_dashboard(dashboard: schemas.DashboardCreate, id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = await chk_access(access_token)
    update_dash = await func_dash.update_dashboard(sess = sess, dash_id = id, dashboard = dashboard, user_id = user_id)
    if update_dash:
        return update_dash
    raise HTTPException(status_code=400, detail="Already Existed Name")

@router.post("/delete")
async def delete_dashboard(id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = await chk_access(access_token)
    if not await func_dash.delete_dashboard(sess = sess, dash_id = id, user_id = user_id):
        raise HTTPException(status_code=400, detail="Not your dashboard")

@router.get("/get")
async def get_dashboard(id: int, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = await chk_access(access_token)
    dash = await func_dash.get_dashboard(sess = sess, dash_id = id, user_id = user_id)
    if dash:
        return dash
    return HTTPException(status_code=400, detail="Cannot Get")

@router.get("/list")
async def list_dashboard(cursor: schemas.Cursor = schemas.Cursor(), pgsize: int = 10, sess: AsyncSession = Depends(get_db_session), access_token: Annotated[str | None, Header()] = None):
    user_id = await chk_access(access_token)
    return await func_dash.list_dashboard(sess = sess, user_id = user_id, cursor = cursor, pgsize = pgsize)