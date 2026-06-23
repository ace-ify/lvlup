import redis
import json
import hashlib
import joblib
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, db=0, protocol=2)

model = joblib.load('model.joblib')


class IrisFlower(BaseModel):
    SepalLengthCm: float
    SepalWidthCm: float
    PetalLengthCm: float
    PetalWidthCm: float

    def to_list(self):
        return [
            self.SepalLengthCm,
            self.SepalWidthCm,
            self.PetalLengthCm,
            self.PetalWidthCm
        ]
    
    def cache_key(self):
        raw = json.dumps(self.model_dump(), sort_keys=True)
        return f"Predict: {hashlib.sha256(raw.encode()).hexdigest()}"
    

@app.post('/predict')
async def predict(data: IrisFlower):
    key = data.cache_key()

    cached_result = redis_client.get(key)
    if cached_result:
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{now}] Serving prediction from Cache!")
        result = json.loads(cached_result)
        result['served_at'] = now
        result['source'] = 'Redis Cache'
        return result
    
    # Simulate ML model prediction
    prediction = model.predict([data.to_list()])[0]
    
    from datetime import datetime
    fetched_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    result = {
        'prediction': int(prediction),
        'fetched_at': fetched_time,
        'source': 'ML Model'
    }
    
    redis_client.set(key, json.dumps(result), ex=3600)
    print(f"[{fetched_time}] Model predicted and saved in Cache!")
    return result