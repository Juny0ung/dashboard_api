from fastapi import FastAPI
from .api import user, post, dashboard
from .api.db import models, crud, schemas
from .api.db.base import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router, prefix='/user')
app.include_router(dashboard.router, prefix='/dashboard')
app.include_router(post.router, prefix='/post')

@app.get("/hi")
def log_in():
    return {"error": "hi"}

