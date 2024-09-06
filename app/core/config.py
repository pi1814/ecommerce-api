from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "E-commerce API"
    MONGODB_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()