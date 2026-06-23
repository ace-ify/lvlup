from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import engine, Base, SessionLocal
from app.db import models
from app import schemas
from app.core import security
from fastapi.security import OAuth2PasswordRequestForm


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ML Prediction API", version="1.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Welcome to ML Prediction API"}

@app.post("/signup", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Username already registered"
        )
    
    hashed_pwd = security.get_password_hash(user.password)
    
    new_user = models.User(username=user.username, hashed_password=hashed_pwd)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not user or not security.verfy_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}
