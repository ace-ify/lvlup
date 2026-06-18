from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # PRODUCTION FIX: Never hardcode frontend domains. Use environment variables (.env) 
    # to load different allowed origins for development (localhost) and production (real domain).
    #
    # Example:
    # from pydantic_settings import BaseSettings
    # class Settings(BaseSettings):
    #     cors_origins: list[str] = ["https://my-frontend.com"]
    #     class Config:
    #         env_file = ".env"
    # settings = Settings()
    # allow_origins=settings.cors_origins,
    allow_origins=[
        'https://my-frontend.com', 'http://localhost:3000'
    ],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['*']
)

# define endpoints