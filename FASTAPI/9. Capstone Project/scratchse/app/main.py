from fastapi import FastAPI
from app.db.database import engine
from app.db import models

from app.api.routes_auth import router as auth_router
from app.api.routes_predict import router as predict_router
from app.middleware.logging_middleware import LoggingMiddleware

# Create tables (In production, use Alembic instead)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ML Prediction API (Modular)", version="2.0")

# Add Middlewares
app.add_middleware(LoggingMiddleware)

# Include Routers
app.include_router(auth_router)
app.include_router(predict_router)

@app.get("/")
def root():
    return {"message": "Welcome to Enterprise ML Prediction API"}