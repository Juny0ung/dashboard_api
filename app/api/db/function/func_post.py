from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import models, schemas
from .func_dash import get_dashboard_by_id

async def is_valid_dash(sess: AsyncSession, dash_id: int, user_id: int):
    dash = await get_dashboard_by_id(sess = sess, id = dash_id)
    if dash and (dash.public or dash.creator_id == user_id):
        return True
    return False

async def get_post_by_id(sess: AsyncSession, id: int):
    async with sess as db:
        stmt = select(models.Post).filter(models.Post.id == id)
        result = await db.execute(stmt)
        return result.scalars().first()

async def create_post(sess: AsyncSession, post: schemas.PostCreate, user_id: int, dash_id: int):
    async with sess as db:
        db_dash = await get_dashboard_by_id(sess = db, id = dash_id)
        if db_dash and (db_dash.public or db_dash.creator_id == user_id):
            db_dash.posts_cnt += 1
            db.add(db_dash)
            db_post = models.Post(**post.dict(), writer_id = user_id, dashboard_id = dash_id)
            db.add(db_post)
            await db.commit()
            await db.refresh(db_post)
            return db_post
    

async def update_post(sess: AsyncSession, post_id: int, post: schemas.PostCreate, user_id: int):
    async with sess as db:
        db_post = await get_post_by_id(sess = db, id = post_id)
        if db_post and db_post.writer_id == user_id:
            db_post.title = post.title
            db_post.content = post.content
            db.add(db_post)
            await db.commit()
            await db.refresh(db_post)
            return db_post
        return None

async def delete_post(sess: AsyncSession, post_id: int, user_id: int):
    async with sess as db:
        db_post = await get_post_by_id(sess = db, id = post_id)

        if db_post and db_post.writer_id == user_id:
            db_dash = await get_dashboard_by_id(sess = db, id = db_post.dashboard_id)
            db_dash.posts_cnt -= 1
            db.add(db_dash)
            await db.delete(db_post)
            await db.commit()
            return True
        return False

async def get_post(sess: AsyncSession, post_id: int, user_id: int):
    async with sess as db:
        db_post = await get_post_by_id(sess = db, id = post_id)

        if db_post and await is_valid_dash(sess = db, dash_id = db_post.dashboard_id, user_id = user_id):
            return db_post
        return None

async def list_post(sess: AsyncSession, dash_id: int, user_id: int, cursor: schemas.Cursor, pgsize: int):
    async with sess as db:
        if await is_valid_dash(sess = db, dash_id = dash_id, user_id = user_id):
            stmt = select(models.Post).order_by(models.Post.id).filter(models.Post.dashboard_id == dash_id)
            if cursor.id:
                stmt = stmt.filter(models.Post.id > cursor.id)
            stmt = stmt.limit(pgsize)
            result = await db.execute(stmt)
            db_posts = result.scalars().all()

            if db_posts:
                next_cursor = {
                    "id": db_posts[-1].id
                }
            else:
                next_cursor = {}
            return {"results" : db_posts, "next_cursor" : next_cursor, "current_cursor" : cursor}