from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from app.db.models import User, SearchHistory, ImageHistory, RefreshToken
from app.schemas.user import UserCreate
from app.core.password import get_password_hash 

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Search History CRUD operations
def create_search_history(
    db: Session, 
    user_id: int, 
    query: str, 
    results: dict, 
    meta_data: dict = None
):
    db_search = SearchHistory(
        user_id=user_id,
        query=query,
        results=results,
        meta_data=meta_data or {}
    )
    db.add(db_search)
    db.commit()
    db.refresh(db_search)
    return db_search

def get_user_search_history(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 10
):
    return db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id
    ).order_by(desc(SearchHistory.created_at)).offset(skip).limit(limit).all()

def delete_search_history(db: Session, search_id: int, user_id: int):
    search = db.query(SearchHistory).filter(
        SearchHistory.id == search_id,
        SearchHistory.user_id == user_id
    ).first()
    if search:
        db.delete(search)
        db.commit()
        return True
    return False

# Image History CRUD operations
def create_image_history(
    db: Session,
    user_id: int,
    prompt: str,
    image_url: str = None,
    image_data: str = None,
    meta_data: dict = None
):
    db_image = ImageHistory(
        user_id=user_id,
        prompt=prompt,
        image_url=image_url,
        image_data=image_data,
        meta_data=meta_data or {}
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def get_user_image_history(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10
):
    return db.query(ImageHistory).filter(
        ImageHistory.user_id == user_id
    ).order_by(desc(ImageHistory.created_at)).offset(skip).limit(limit).all()

def delete_image_history(db: Session, image_id: int, user_id: int):
    image = db.query(ImageHistory).filter(
        ImageHistory.id == image_id,
        ImageHistory.user_id == user_id
    ).first()
    if image:
        db.delete(image)
        db.commit()
        return True
    return False

def save_refresh_token(db: Session, user_id: int, token: str):
    db_token = RefreshToken(user_id=user_id, token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def delete_refresh_token(db: Session, token: str):
    db.query(RefreshToken).filter(RefreshToken.token == token).delete()
    db.commit()

def get_image_history(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(ImageHistory).filter(ImageHistory.user_id == user_id).offset(skip).limit(limit).all()
