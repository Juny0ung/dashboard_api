from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from access_token import get_user_id

from .db import models, schemas, crud

# Dependency
from .db.base import SessionLocal
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()


@router.post("/create", tags=["post"])
def create_dashboard(dashboard: schemas.DashboardCreate, token: str, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Access")
    if crud.get_dashboard_by_name(db = db, name = dashboard.name):
        raise HTTPException(status_code=400, detail="Already Existed Name")
    return crud.create_dashboard(db = db, dashboard = dashboard, creator = user_id)

@router.put("/update", tags=["put"])
def update_dashboard(dash_id: int, name: str, public: bool, token: str, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Access")
    update_dash = crud.update_dashboard(db = db, dash_id = dash_id, name = name, public = public, user_id = user_id)
    if update_dash:
        return update_dash
    raise HTTPException(status_code=400, detail="Already Existed Name")

@router.post("/delete", tags=["post"])
def delete_dashboard(dash_id: int, token: str, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Access")
    return crud.delete_dashboard(db = db, dash_id = dash_id, user_id = user_id)

@router.get("/get", tags=["get"])
def get_dashboard(dash_id: int, token: str, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Access")
    dash = crud.get_dashboard(db = db, dash_id = dash_id, user_id = user_id)
    if dash:
        return dash
    return HTTPException(status_code=400, detail="Fail")

@router.get("/list", tags=["get"])
def list_dashboard(token: str, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid Access")
    return crud.list_dashboard(db = db, user_id = user_id)