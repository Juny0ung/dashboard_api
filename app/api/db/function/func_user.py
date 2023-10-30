import hashlib
import string
import random
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import models, schemas

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
        raise HTTPException(status_code=400, detail="Wrong Information")

async def create_user(sess: AsyncSession, user: schemas.UserCreate):
    salt, hash_pw = hash_password(user.password)
    async with sess as db:
        db_user = models.User(email = user.email, hash_password = hash_pw, fullname = user.fullname, salt = salt)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return schemas.UserInfo.from_orm(db_user)