from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_
from sqlalchemy.future import select
from fastapi import HTTPException
from typing import List
from .. import models, schemas

async def get_dashboard_by_name(sess: AsyncSession, name: str):
    async with sess as db:
        stmt = select(models.Dashboard).filter(models.Dashboard.name == name)
        result = await db.execute(stmt)
        return result.scalars().first()

async def get_dashboard_by_id(sess: AsyncSession, id: int):
    async with sess as db:
        stmt = select(models.Dashboard).filter(models.Dashboard.id == id)
        result = await db.execute(stmt)
        return result.scalars().first()
 
async def create_dashboard(sess: AsyncSession, dashboard: schemas.DashboardCreate, creator: str):
    async with sess as db:
        db_dash = models.Dashboard(**dashboard.dict(), creator_id = creator, posts_cnt = 0)
        db.add(db_dash)
        await db.commit()
        await db.refresh(db_dash)
        return schemas.DashboardInfo.from_orm(db_dash)

async def update_dashboard(sess: AsyncSession, dash_id: int, dashboard: schemas.DashboardCreate, user_id: int):
    async with sess as db:
        db_dash = await get_dashboard_by_name(sess = db, name = dashboard.name)
        if db_dash and db_dash.id != dash_id:
            raise HTTPException(status_code=400, detail="Already Existed Name")
        elif not db_dash:
            db_dash = await get_dashboard_by_id(sess = db, id = dash_id)
        _assert_valid(db_dash = db_dash, user_id = user_id)
        print(db_dash)
        db_dash.name = dashboard.name
        db_dash.public = dashboard.public
        db.add(db_dash)
        await db.commit()
        await db.refresh(db_dash)
        return schemas.DashboardInfo.from_orm(db_dash)

async def delete_dashboard(sess: AsyncSession, dash_id: int, user_id: int):
    async with sess as db:
        db_dash = await get_dashboard_by_id(sess = db, id = dash_id)
        _assert_valid(db_dash = db_dash, user_id = user_id)

        res = schemas.DashboardInfo.from_orm(db_dash)
        await db.delete(db_dash)
        await db.commit()
        return res

async def get_dashboard(sess: AsyncSession, dash_id: int, user_id: int):
    db_dash = await get_dashboard_by_id(sess = sess, id = dash_id)
    _assert_valid(db_dash = db_dash, user_id = user_id, isView = True)
    return schemas.DashboardInfo.from_orm(db_dash)

async def list_dashboard(sess: AsyncSession, user_id: int, cursor: str, pgsize: int):
    cvals = cursor.split("_")
    is_sort = int(cvals[0])
    async with sess as db:
        if is_sort == 1:
            stmt = _query_ordered_by_posts_cnt(cursor = cvals)
        else:
            stmt = _query_ordered_by_id(cursor = cvals)
        stmt = stmt.filter(or_(models.Dashboard.creator_id == user_id, models.Dashboard.public)).limit(pgsize)
        result = await db.execute(stmt)
        db_dashes = result.scalars().all()

        if db_dashes:
            if is_sort == 1:
                next_cursor = _next_cursor_ordered_by_posts_cnt(db_dashes[-1])
            else:
                next_cursor = _next_cursor_ordered_by_id(db_dashes[-1])
        else:
            next_cursor = "0"

        return {"results": [schemas.DashboardInfo.from_orm(db_dash) for db_dash in db_dashes], "next_cursor": next_cursor, "current_cursor" : cursor}

def _assert_valid(db_dash: schemas.Dashboard, user_id: int, isView: bool = False):
    if db_dash == None:
        raise HTTPException(status_code = 400, detail = "No Such Dashboard")
    if db_dash.creator_id != user_id:
        if isView:
            if db_dash.public:
                return
            else:
                raise HTTPException(status_code = 400, detail = "Not Public Dashboard")
        raise HTTPException(status_code = 400, detail = "Not Your Dashboard")
    


def _query_ordered_by_id(cursor: List[str]):
    stmt = select(models.Dashboard).order_by(models.Dashboard.id)
    if len(cursor) > 1:
        tid = int(cursor[1])
        stmt = stmt.filter(models.Dashboard.id > tid)
    return stmt

def _next_cursor_ordered_by_id(db_dash: schemas.Dashboard):
    return f"0_{db_dash.id}"

def _query_ordered_by_posts_cnt(cursor: List[str]):
    stmt = select(models.Dashboard).order_by(models.Dashboard.posts_cnt.desc()).order_by(models.Dashboard.id)
    if len(cursor) > 1:
        tcnt = int(cursor[1])
        tid = int(cursor[2])
        stmt = stmt.filter(or_(models.Dashboard.posts_cnt < tcnt, and_(models.Dashboard.posts_cnt == tcnt, models.Dashboard.id > tid)))
    return stmt

def _next_cursor_ordered_by_posts_cnt(db_dash: schemas.Dashboard):
    return f"1_{db_dash.posts_cnt}_{db_dash.id}"