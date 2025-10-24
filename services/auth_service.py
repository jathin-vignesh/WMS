from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from utils.auth_helper import hash_password, verify_password, create_access_token, create_refresh_token
from models.models import User,UserRole
from schemas import auth_schema as schemas


def register_user(db: Session, user_in: schemas.UserCreate):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.name == user_in.name).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    db_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role=user_in.role or UserRole.staff
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def login_user(db: Session, form_data: schemas.UserLogin):
    user = db.query(User).filter(
        (User.email == form_data.username_or_email) |
        (User.name == form_data.username_or_email)
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token_data = {"user_id": user.id, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def update_user_info(db: Session, user_id: int, user_update: schemas.UserUpdate, current_user):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")


    if current_user.role.value != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You are not allowed to update other users")


    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.email is not None:
        db_user.email = user_update.email
    if user_update.password is not None:
        db_user.password_hash = hash_password(user_update.password)
    if current_user.role.value == "admin" and user_update.role is not None:
        db_user.role = user_update.role

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user_account(db: Session, user_id: int, current_user):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete users")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return None