import hashlib
import string
import random
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from . import models, schemas

# user

def hash_password(pw: str, salt: str | None = None):
    if salt == None:
        salt = "".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k = 16))
    for _ in range(100):
        pw = hashlib.sha256((pw + salt).encode()).hexdigest()
    return salt, pw

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 0):
    return db.query(models.User).offset(skip).limit(limit).all()

def auth_user(db: Session, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if hash_password(user.password, db_user.salt)[1] == db_user.hash_password:
        return db_user.id
    return None

def create_user(db: Session, user: schemas.UserCreate):
    salt, hash_pw = hash_password(user.password)
    db_user = models.User(email = user.email, hash_password = hash_pw, fullname = user.fullname, salt = salt)
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
    db_dash = models.Dashboard(**dashboard.dict(), creator_id = creator, posts_cnt = 0)
    db.add(db_dash)
    db.commit()
    db.refresh(db_dash)
    return db_dash

def update_dashboard(db: Session, dash_id: int, dashboard: schemas.DashboardCreate, user_id: int):
    db_dash = get_dashboard_by_name(db = db, name = dashboard.name)
    if db_dash and db_dash.id != dash_id:
        return None
    db_dash = get_dashboard_by_id(db = db, id = dash_id)
    db_dash.name = dashboard.name
    db_dash.public = dashboard.public
    db.add(db_dash)
    db.commit()
    db.refresh(db_dash)
    return db_dash

def delete_dashboard(db: Session, dash_id: int, user_id: int):
    db_dash = get_dashboard_by_id(db = db, id = dash_id)

    if db_dash and db_dash.creator_id == user_id:
        db.delete(db_dash)
        db.commit()
        return True
    return False

def get_dashboard(db: Session, dash_id: int, user_id: int):
    db_dash = db.query(models.Dashboard).filter(models.Dashboard.id == dash_id).first()

    if db_dash and (db_dash.public or db_dash.creator_id == user_id):
        return db_dash
    return None

def list_dashboard(db: Session, user_id: int, cursor: schemas.Cursor, pgsize: int):
    
    if cursor.is_sort == 1:
        query = _list_dashboard_query_by_posts_cnt(db = db, cursor = cursor)
    else:
        query = _list_dashboard_query_by_id(db = db, cursor = cursor)
    
    db_dashes = query.filter(or_(models.Dashboard.creator_id == user_id, models.Dashboard.public)).limit(pgsize).all()

    if db_dashes:
        if cursor.is_sort == 1:
            next_cursor = _list_dashboard_next_cursor_by_posts_cnt(db_dashes[-1])
        else:
            next_cursor = _list_dashboard_next_cursor_by_id(db_dashes[-1])
    else:
        next_cursor = {}

    return {"results": db_dashes, "next_cursor": next_cursor}

def _list_dashboard_query_by_id(db: Session, cursor: schemas.Cursor):
    query = db.query(models.Dashboard).order_by(models.Dashboard.id)
    if cursor.id:
        query = query.filter(models.Dashboard.id > cursor.id)
    return query

def _list_dashboard_next_cursor_by_id(db_dash: schemas.Dashboard):
    return {
        "is_sort" : 0,
        "id" : db_dash.id
    }

def _list_dashboard_query_by_posts_cnt(db: Session, cursor: schemas.Cursor):
    query = db.query(models.Dashboard).order_by(models.Dashboard.posts_cnt.desc()).order_by(models.Dashboard.id)
    if cursor.posts_cnt:
        query = query.filter(or_(models.Dashboard.posts_cnt < cursor.posts_cnt, and_(models.Dashboard.posts_cnt == cursor.posts_cnt, models.Dashboard.id > cursor.id)))
    return query

def _list_dashboard_next_cursor_by_posts_cnt(db_dash: schemas.Dashboard):
    return {
        "is_sort" : 1,
        "posts_cnt" : db_dash.posts_cnt,
        "id" : db_dash.id
    }

# post

def is_valid_dash(db: Session, dash_id: int, user_id: int):
    dash = get_dashboard_by_id(db = db, id = dash_id)
    if dash and (dash.public or dash.creator_id == user_id):
        return True
    return False

def get_post_by_id(db: Session, id: int):
    return db.query(models.Post).filter(models.Post.id == id).first()

def create_post(db: Session, post: schemas.PostCreate, user_id: int, dash_id: int):
    db_dash = get_dashboard_by_id(db = db, id = dash_id)
    if db_dash and (db_dash.public or db_dash.creator_id == user_id):
        db_dash.posts_cnt += 1
        db.add(db_dash)
        db_post = models.Post(**post.dict(), writer_id = user_id, dashboard_id = dash_id)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post
    

def update_post(db: Session, post_id: int, post: schemas.PostCreate, user_id: int):
    db_post = get_post_by_id(db = db, id = post_id)
    if db_post and db_post.writer_id == user_id:
        db_post.title = post.title
        db_post.content = post.content
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post
    return None

def delete_post(db: Session, post_id: int, user_id: int):
    db_post = get_post_by_id(db = db, id = post_id)

    if db_post and db_post.writer_id == user_id:
        db_dash = get_dashboard_by_id(db = db, id = db_post.dashboard_id)
        db_dash.posts_cnt -= 1
        db.add(db_dash)
        db.delete(db_post)
        db.commit()
        return True
    return False

def get_post(db: Session, post_id: int, user_id: int):
    db_post = get_post_by_id(db = db, id = post_id)

    if db_post and is_valid_dash(db = db, dash_id = db_post.dashboard_id, user_id = user_id):
        return db_post
    return None

def list_post(db: Session, dash_id: int, user_id: int, cursor: schemas.Cursor, pgsize: int):
    if is_valid_dash(db = db, dash_id = dash_id, user_id = user_id):
        query = db.query(models.Post).order_by(models.Post.id).filter(models.Post.dashboard_id == dash_id)
        if cursor.id:
            query = query.filter(models.Post.id > cursor.id)
        db_posts = query.limit(pgsize).all()
        if db_posts:
            next_cursor = {
                "id": db_posts[-1].id
            }
        else:
            next_cursor = {}
        return {"results" : db_posts, "next_cursor" : next_cursor}