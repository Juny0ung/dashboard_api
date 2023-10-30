from fastapi import FastAPI
from .api.router import user, post, dashboard
from .api.db import models
from .api.db.base import engine
from .api.token import init_redis, close_redis

app = FastAPI()

app.include_router(user.router, prefix='/user')
app.include_router(dashboard.router, prefix='/dashboard')
app.include_router(post.router, prefix='/post')

@app.get("/hi")
def log_in():
    return {"error": "hi"}

@app.on_event("startup")
async def startup_event():
    await init_redis()
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()
    await engine.dispose()
