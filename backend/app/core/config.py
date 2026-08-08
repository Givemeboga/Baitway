from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://baitway_admin:baitway_password@localhost:5432/baitway"
    jwt_secret: str = "change_moi_avant_prod"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    class Config:
        env_file = ".env"

settings = Settings()