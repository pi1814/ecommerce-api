from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from app.api.dependencies import get_db, get_current_active_user, get_current_admin_user
from app.schemas.user import UserCreate, UserUpdate, UserOut, Token
from app.services.user_service import UserService
from app.core.security import create_access_token
from app.core.config import settings
from datetime import timedelta
from typing import List

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorClient = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncIOMotorClient = Depends(get_db)):
    user_service = UserService(db)
    existing_user = await user_service.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return user_service.serialize_to_user_out(await user_service.create_user(user))

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: UserOut = Depends(get_current_active_user), db: AsyncIOMotorClient = Depends(get_db)):
    user_service = UserService(db)
    return user_service.serialize_to_user_out(current_user)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, db: AsyncIOMotorClient = Depends(get_db), current_user: UserOut = Depends(get_current_active_user)):
    user_service = UserService(db)
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user_service.serialize_to_user_out(user)

@router.get("/", response_model=List[UserOut])
async def get_users(skip: int = 0, limit: int = 10, db: AsyncIOMotorClient = Depends(get_db), current_user: UserOut = Depends(get_current_admin_user)):
    user_service = UserService(db)
    return await user_service.get_users(skip, limit)

@router.put("/{user_id}", response_model=UserOut)
async def update_user(user_id: str, user_update: UserUpdate, db: AsyncIOMotorClient = Depends(get_db), current_user: UserOut = Depends(get_current_active_user)):
    user_service = UserService(db)
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    updated_user = await user_service.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user_service.serialize_to_user_out(updated_user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: AsyncIOMotorClient = Depends(get_db), current_user: UserOut = Depends(get_current_admin_user)):
    user_service = UserService(db)
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )