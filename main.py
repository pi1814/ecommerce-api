from fastapi import FastAPI
from app.api.endpoints import users, products, shopping_carts
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from app.api.dependencies import get_db
from app.schemas.user import Token
from app.services.user_service import UserService
from app.core.security import create_access_token
from app.core.config import settings
from datetime import timedelta

app = FastAPI(title=settings.APP_NAME)

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(shopping_carts.router, prefix="/shopping-carts", tags=["shopping_carts"])

@app.get("/")
async def root():
    return {"message": "Welcome to the E-commerce API"}

@app.post("/token", response_model=Token)
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