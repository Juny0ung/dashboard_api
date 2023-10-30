from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_
from sqlalchemy.future import select
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
        return db_dash

async def update_dashboard(sess: AsyncSession, dash_id: int, dashboard: schemas.DashboardCreate, user_id: int):
    async with sess as db:
        db_dash = await get_dashboard_by_name(sess = db, name = dashboard.name)
        if db_dash and db_dash.id != dash_id:
            return None
        elif not db_dash:
            db_dash = await get_dashboard_by_id(sess = db, id = dash_id)
        db_dash.name = dashboard.name
        db_dash.public = dashboard.public
        db.add(db_dash)
        await db.commit()
        await db.refresh(db_dash)
        return db_dash

async def delete_dashboard(sess: AsyncSession, dash_id: int, user_id: int):
    async with sess as db:
        db_dash = await get_dashboard_by_id(sess = db, id = dash_id)

        if db_dash and db_dash.creator_id == user_id:
            await db.delete(db_dash)
            await db.commit()
            return True
        return False

async def get_dashboard(sess: AsyncSession, dash_id: int, user_id: int):
    async with sess as db:
        stmt = select(models.Dashboard).filter(and_(models.Dashboard.id == dash_id, or_(models.Dashboard.public, models.Dashboard.creator_id == user_id)))
        result = await db.execute(stmt)
        return result.scalars().first()

async def list_dashboard(sess: AsyncSession, user_id: int, cursor: schemas.Cursor, pgsize: int):
    async with sess as db:
        if cursor.is_sort == 1:
            stmt = _list_dashboard_query_by_posts_cnt(cursor = cursor)
        else:
            stmt = _list_dashboard_query_by_id(cursor = cursor)
        stmt = stmt.filter(or_(models.Dashboard.creator_id == user_id, models.Dashboard.public)).limit(pgsize)
        result = await db.execute(stmt)
        db_dashes = result.scalars().all()

        if db_dashes:
            if cursor.is_sort == 1:
                next_cursor = _list_dashboard_next_cursor_by_posts_cnt(db_dashes[-1])
            else:
                next_cursor = _list_dashboard_next_cursor_by_id(db_dashes[-1])
        else:
            next_cursor = {}

        return {"results": db_dashes, "next_cursor": next_cursor, "current_cursor" : cursor}

def _list_dashboard_query_by_id(cursor: schemas.Cursor):
    stmt = select(models.Dashboard).order_by(models.Dashboard.id)
    if cursor.id:
        stmt = stmt.filter(models.Dashboard.id > cursor.id)
    return stmt

def _list_dashboard_next_cursor_by_id(db_dash: schemas.Dashboard):
    return {
        "is_sort" : 0,
        "id" : db_dash.id
    }

def _list_dashboard_query_by_posts_cnt(cursor: schemas.Cursor):
    stmt = select(models.Dashboard).order_by(models.Dashboard.posts_cnt.desc()).order_by(models.Dashboard.id)
    if cursor.posts_cnt != None:
        stmt = stmt.filter(or_(models.Dashboard.posts_cnt < cursor.posts_cnt, and_(models.Dashboard.posts_cnt == cursor.posts_cnt, models.Dashboard.id > cursor.id)))
    return stmt

def _list_dashboard_next_cursor_by_posts_cnt(db_dash: schemas.Dashboard):
    return {
        "is_sort" : 1,
        "posts_cnt" : db_dash.posts_cnt,
        "id" : db_dash.id
    }