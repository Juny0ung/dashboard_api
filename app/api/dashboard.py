from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from .db import models, schemas, crud
from app.api.dependencies import get_db, chk_access

router = APIRouter()


@router.post("/create", tags=["post"])
def create_dashboard(dashboard: schemas.DashboardCreate, db: Session = Depends(get_db), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    if crud.get_dashboard_by_name(db = db, name = dashboard.name):
        raise HTTPException(status_code=400, detail="Already Existed Name")
    return crud.create_dashboard(db = db, dashboard = dashboard, creator = user_id)

@router.put("/update", tags=["put"])
def update_dashboard(dashboard: schemas.DashboardCreate, id: int, db: Session = Depends(get_db), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    update_dash = crud.update_dashboard(db = db, dash_id = id, dashboard = dashboard, user_id = user_id)
    if update_dash:
        return update_dash
    raise HTTPException(status_code=400, detail="Already Existed Name")

@router.post("/delete", tags=["post"])
def delete_dashboard(id: int, db: Session = Depends(get_db), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    if not crud.delete_dashboard(db = db, dash_id = id, user_id = user_id):
        raise HTTPException(status_code=400, detail="Not your dashboard")

@router.get("/get", tags=["get"])
def get_dashboard(id: int, db: Session = Depends(get_db), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    dash = crud.get_dashboard(db = db, dash_id = id, user_id = user_id)
    if dash:
        return dash
    return HTTPException(status_code=400, detail="Cannot Get")

@router.get("/list", tags=["get"])
def list_dashboard(cursor: schemas.Cursor = schemas.Cursor(), pgsize: int = 10, db: Session = Depends(get_db), access_token: Annotated[str | None, Header()] = None):
    user_id = chk_access(access_token)
    return crud.list_dashboard(db = db, user_id = user_id, cursor = cursor, pgsize = pgsize)