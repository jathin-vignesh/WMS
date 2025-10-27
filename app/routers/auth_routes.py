from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import auth_schema as schemas
from services import auth_service as crud_operations
from utils.auth_helper import get_current_user_and_db
from db import get_db

router = APIRouter(tags=["Auth"])

@router.post("/auth/register", response_model=schemas.UserResponse, status_code=200)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud_operations.register_user(db, user_in)

@router.post("/auth/login", response_model=schemas.TokenResponse)
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    return crud_operations.login_user(db, form_data)

@router.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user=Depends(get_current_user_and_db)):
    user,db= current_user
    return user

@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_and_db),
):
    user,d = current_user
    return crud_operations.update_user_info(db, user_id, user_update, user)

@router.delete("/users/{user_id}", status_code=200)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_and_db),
):
    user,d = current_user
    return crud_operations.delete_user_account(db, user_id, user)