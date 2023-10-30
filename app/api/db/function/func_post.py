from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from .. import models, schemas
from .func_dash import _get_dashboard_by_id

async def get_valid_dash(sess: AsyncSession, dash_id: int, user_id: int):
    dash = await _get_dashboard_by_id(sess = sess, id = dash_id)
    if dash and (dash.public or dash.creator_id == user_id):
        return dash
    raise HTTPException(status_code=400, detail="Invalid Dashboard")

async def get_post_by_id(sess: AsyncSession, id: int):
    async with sess as db:
        stmt = select(models.Post).filter(models.Post.id == id)
        result = await db.execute(stmt)
        return result.scalars().first()

async def create_post(sess: AsyncSession, post: schemas.PostCreate, user_id: int, dash_id: int):
    async with sess as db:
        db_dash = await get_valid_dash(sess = db, dash_id = dash_id, user_id = user_id)
        db_dash.posts_cnt += 1
        db.add(db_dash)
        db_post = models.Post(**post.dict(), writer_id = user_id, dashboard_id = dash_id)
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        return schemas.Post.from_orm(db_post)
    
def _assert_valid(db_post: schemas.Post, user_id: int):
    if not db_post:
        raise HTTPException(status_code=400, detail="No Such Post")
    if db_post.writer_id != user_id:
        raise HTTPException(status_code=400, detail="Not Your Post")

async def update_post(sess: AsyncSession, post_id: int, post: schemas.PostCreate, user_id: int):
    async with sess as db:
        db_post = await get_post_by_id(sess = db, id = post_id)
        _assert_valid(db_post = db_post, user_id = user_id)
        db_post.title = post.title
        db_post.content = post.content
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        return schemas.Post.from_orm(db_post)
    
async def delete_post(sess: AsyncSession, post_id: int, user_id: int):
    async with sess as db:
        db_post = await get_post_by_id(sess = db, id = post_id)
        _assert_valid(db_post = db_post, user_id = user_id)
        db_dash = await _get_dashboard_by_id(sess = db, id = db_post.dashboard_id)
        db_dash.posts_cnt -= 1
        db.add(db_dash)
        res = schemas.Post.from_orm(db_post)
        await db.delete(db_post)
        await db.commit()
        return res

async def get_post(sess: AsyncSession, post_id: int, user_id: int):
    async with sess as db:
        db_post = await get_post_by_id(sess = db, id = post_id)
        if not db_post:
            raise HTTPException(status_code=400, detail="No Such Post")

        await get_valid_dash(sess = db, dash_id = db_post.dashboard_id, user_id = user_id)
        return schemas.Post.from_orm(db_post)

async def list_post(sess: AsyncSession, dash_id: int, user_id: int, cursor: str, pgsize: int):
    cid = int(cursor)
    async with sess as db:
        await get_valid_dash(sess = db, dash_id = dash_id, user_id = user_id)
        stmt = select(models.Post).order_by(models.Post.id).filter(models.Post.dashboard_id == dash_id)
        if cid > 0:
            stmt = stmt.filter(models.Post.id > cid)
        stmt = stmt.limit(pgsize)
        result = await db.execute(stmt)
        db_posts = result.scalars().all()

        if db_posts:
            next_cursor = str(db_posts[-1].id)
        else:
            next_cursor = "0"
        return {"results" : [schemas.Post.from_orm(db_post) for db_post in db_posts], "next_cursor" : next_cursor, "current_cursor" : cursor}