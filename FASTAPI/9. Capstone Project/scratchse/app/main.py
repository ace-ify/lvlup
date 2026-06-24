from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import engine, Base, SessionLocal
from app.db import models
from jose import jwt, JWTError
from app import schemas
from app.core import security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.core.config import settings
import json
import redis
import time
from fastapi import Request



models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ML Prediction API", version="1.0")
try:
    redis_client = redis.Redis(
        host=settings.redis_host, 
        port=settings.redis_port, 
        decode_responses=True,
        protocol=2
    )
    redis_client.ping() # Connection test
except redis.ConnectionError:
    redis_client = None
    print("Warning: Redis is not running. Caching is disabled.")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user=db.query(models.User).filter(models.User.username == username).first()
    
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
            status_code=429, # 429 = Too Many Requests
            detail="Rate limit exceeded. Try again in a minute."
        )
        
    redis_client.zadd(key, {str(current_time): current_time})
    redis_client.expire(key, WINDOW_SECONDS)
    
    return current_user


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


@app.post("/predict", response_model=schemas.PredictionResponse)
def predict_car_price(
    features: schemas.CarFeatures, 
    current_user: models.User = Depends(check_rate_limit), # Guard lag gaya!
    db: Session = Depends(get_db) # Naya: Database dependency add ki
):
    cache_key = f"predict:{features.year}:{features.mileage}:{features.engine_size}"
    
    if redis_client:
        cached_result = redis_client.get(cache_key)
        if cached_result:
            print("🚀 Serving from FAST Redis Cache!")
            result = json.loads(cached_result)
            
            # Cache hit par bhi log save karna zaroori hai audit ke liye
            log_entry = models.PredictionLog(
                username=current_user.username,
                features_hash=cache_key,
                prediction_result=result["prediction"]
            )
            db.add(log_entry)
            db.commit()
            
            return result

    print("⏳ Calculating using ML Model...")
    base_price = 50000
    age_penalty = (2025 - features.year) * 1000
    mileage_penalty = features.mileage * 0.1
    engine_bonus = features.engine_size * 5000
    
    final_prediction = base_price - age_penalty - mileage_penalty + engine_bonus
    
    if final_prediction < 1000:
        final_prediction = 1000
        
    result = {
        "prediction": round(final_prediction, 2),
        "model_version": "v1.0 (Mock)"
    }

    if redis_client:
        redis_client.setex(cache_key, 3600, json.dumps(result))
        
    # Naya: Prediction ko database mein save karo (Cache Miss hone par)
    log_entry = models.PredictionLog(
        username=current_user.username,
        features_hash=cache_key,
        prediction_result=result["prediction"]
    )
    db.add(log_entry)
    db.commit()

    return result