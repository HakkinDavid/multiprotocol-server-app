from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    EMAIL_PASSWORD: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour expiration

    class Config:
        env_file = "app/.env"

settings = Settings()
