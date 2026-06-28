from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str
    environment: str
    debug: bool
    jwt_secret_key: str
    access_token_expire_minutes: int
    redis_host: str
    redis_port: int
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()
