from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://developer:devpassword@127.0.0.1:25000/developer"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo = True)

Base = declarative_base()

async def get_db_session():
    asyncsession = AsyncSession(bind = engine)
    try:
        yield asyncsession
    finally:
        await asyncsession.close()