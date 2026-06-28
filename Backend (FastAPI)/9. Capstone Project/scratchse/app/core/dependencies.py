import time
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.database import SessionLocal
from app.db import models
from app.core import security
from app.core.config import settings
from app.cache.redis_cache import redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def check_rate_limit(request: Request, current_user: models.User = Depends(get_current_user)):
    if not redis_client:
        return current_user
        
    MAX_REQUESTS = 5
    WINDOW_SECONDS = 60
    
    key = f"rate_limit:{current_user.username}"
    current_time = time.time()
    
    redis_client.zremrangebyscore(key, 0, current_time - WINDOW_SECONDS)
    request_count = redis_client.zcard(key)
    
    if request_count >= MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again in a minute."
        )
        
    redis_client.zadd(key, {str(current_time): current_time})
    redis_client.expire(key, WINDOW_SECONDS)
    
    return current_user
