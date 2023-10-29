import hashlib
import string
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_
from sqlalchemy.future import select
from . import models, schemas

# user

def hash_password(pw: str, salt: str | None = None):
    if salt == None:
        salt = "".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k = 16))
    for _ in range(100):
        pw = hashlib.sha256((pw + salt).encode()).hexdigest()
    return salt, pw

async def get_user(sess: AsyncSession, user_id: int):
    async with sess as db:
        stmt = select(models.User).filter(models.User.id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

async def get_user_by_email(sess: AsyncSession, email: str):
    async with sess as db:
        stmt = select(models.User).filter(models.User.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

async def auth_user(sess: AsyncSession, user: schemas.UserCreate):
    async with sess as db:
        stmt = select(models.User).filter(models.User.email == user.email)
        result = await db.execute(stmt)
        db_user = result.scalars().first()
        if hash_password(user.password, db_user.salt)[1] == db_user.hash_password:
            return db_user.id
        return None

async def create_user(sess: AsyncSession, user: schemas.UserCreate):
    salt, hash_pw = hash_password(user.password)
    async with sess as db:
        db_user = models.User(email = user.email, hash_password = hash_pw, fullname = user.fullname, salt = salt)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user



# dashboard

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

# post

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