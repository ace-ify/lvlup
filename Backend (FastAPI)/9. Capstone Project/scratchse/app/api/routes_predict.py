from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

from app import schemas
from app.db import models
from app.core.dependencies import get_db, check_rate_limit
from app.cache.redis_cache import redis_client
from app.services.model_service import calculate_prediction

router = APIRouter(tags=["Prediction"])

@router.post("/predict", response_model=schemas.PredictionResponse)
def predict_car_price(
    features: schemas.CarFeatures, 
    current_user: models.User = Depends(check_rate_limit),
    db: Session = Depends(get_db)
):
    cache_key = f"predict:{features.year}:{features.mileage}:{features.engine_size}"
    
    if redis_client:
        cached_result = redis_client.get(cache_key)
        if cached_result:
            print("🚀 Serving from FAST Redis Cache!")
            result = json.loads(cached_result)
            
            log_entry = models.PredictionLog(
                username=current_user.username,
                features_hash=cache_key,
                prediction_result=result["prediction"]
            )
            db.add(log_entry)
            db.commit()
            
            return result

    print("⏳ Calculating using ML Model...")
    final_prediction = calculate_prediction(features)
        
    result = {
        "prediction": round(final_prediction, 2),
        "model_version": "v1.0 (Mock)"
    }

    if redis_client:
        redis_client.setex(cache_key, 3600, json.dumps(result))
        
    log_entry = models.PredictionLog(
        username=current_user.username,
        features_hash=cache_key,
        prediction_result=result["prediction"]
    )
    db.add(log_entry)
    db.commit()

    return result
