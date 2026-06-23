from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import engine, Base, SessionLocal
from app.db import models
from app import schemas
from app.core import security

models.Base.metadata.create_all(bind=engine)
