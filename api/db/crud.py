from sqlalchemy.orm import Session

from . import models, schemas

# user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 0):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fhp = user.password + "notReallyHashed"
    db_user = models.User(email = user.email, password = fhp)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



# dashboard

def get_dashboard_by_name(db: Session, name: str):
    return db.query(models.Dashboard).filter(models.Dashboard.name == name).first()

def get_dashboard_by_id(db: Session, id: int):
    return db.query(models.Dashboard).filter(models.Dashboard.id == id).first()

def create_dashboard(db: Session, dashboard: schemas.DashboardCreate, creator: str):
    db_dash = models.Dashboard(**dashboard.dict(), creator = creator)
    db.add(db_dash)
    db.commit()
    db.refresh(db_dash)
    return db_dash

def update_dashboard(db: Session, dash_id: int, name: str, public: bool, user_id: int):
    db_dash = get_dashboard_by_name(db = db, name = name)
    if db_dash:
        if db_dash.creator == user_id:
            db_dash.public = public
            db.add(db_dash)
            db.commit()
        else:
            return None
    else:
        db_dash = get_dashboard_by_id(db = db, id = dash_id)
        db_dash.name = name
        db_dash.public = public
        db.add(db_dash)
        db.commit()
    db.refresh(db_dash)
    return db_dash

def delete_dashboard(db: Session, dash_id: int, user_id: int):
    db_dash = get_dashboard_by_id(db = db, id = dash_id)

    if db_dash and db_dash.creator == user_id:
        db.delete(db_dash)
        db.commit()
        return True
    return False

def get_dashboard(db: Session, dash_id: int, user_id: int):
    db_dash = db.query(models.Dashboard).filter(models.Dashboard.id == dash_id).first()

    if db_dash and (db_dash.public or db_dash.creator == user_id):
        return db_dash
    return None

# TODO: how to sort
def list_dashboard(db: Session, user_id: int):
    return db.query(models.Dashboard).filter(models.Dashboard.creator == user_id or models.Dashboard.public)



# post

def is_valid_dash(db: Session, dash_id: int, user_id: int):
    dash = get_dashboard_by_id(db = db, id = dash_id)
    if dash and (dash.public or dash.creator == user_id):
        return True
    return False

def get_post_by_id(db: Session, id: int):
    return db.query(models.Post).filter(models.Post.id == id).first()

def create_post(db: Session, post: schemas.PostCreate, user_id: int, dash_id: int):
    db_post = models.Post(**post.dict(), writer = user_id, dashboard = dash_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def update_post(db: Session, post_id: int, title: str, content: str, user_id: int):
    db_post = get_post_by_id(db = db, id = post_id)
    if db_post and db_post.writer == user_id:
        db_post.title = title
        db_post.content = content
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post
    return None

def delete_post(db: Session, post_id: int, user_id: int):
    db_post = get_post_by_id(db = db, id = post_id)

    if db_post and db_post.writer == user_id:
        db.delete(db_post)
        db.commit()
        return True
    return False

def get_post(db: Session, post_id: int, user_id: int):
    db_post = get_post_by_id(db = db, id = post_id)

    if db_post and is_valid_dash(db = db, dash_id = db_post.dashboard, user_id = user_id):
        return db_post
    return None

def list_post(db: Session, dash_id: int, user_id: int):
    if is_valid_dash(db = db, dash_id = dash_id, user_id = user_id):
        return db.query(models.Post).filter(models.Post.dashboard == dash_id)