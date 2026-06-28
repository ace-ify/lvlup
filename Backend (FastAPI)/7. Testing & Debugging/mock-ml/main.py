import numpy as np
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from model import model

app = FastAPI()


class IrisFlower(BaseModel):
    SepalLengthCm: float
    SepalWidthCm: float
    PetalLengthCm: float
    PetalWidthCm: float


@app.post('/predict')
def predict(data: IrisFlower):
    features = np.array([
        [
            data.SepalLengthCm,
            data.SepalWidthCm,
            data.PetalLengthCm,
            data.PetalWidthCm
        ]
    ])
    prediction = model.predict(features)
    return {'prediction': int(prediction[0])}


@app.get('/get-weather')
def get_weather(city: str):
    # This calls an external weather API that might be slow or require an API key
    url = f"https://api.weatherapi.com/v1/current.json?key=mock-key&q={city}"
    response = httpx.get(url)
    data = response.json()
    temp_c = data['current']['temp_c']
    return {'city': city, 'temperature': temp_c}