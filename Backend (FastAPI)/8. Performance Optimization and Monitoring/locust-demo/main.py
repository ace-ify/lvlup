from fastapi import FastAPI
import time
from pydantic import BaseModel

app = FastAPI()


class InputData(BaseModel):
    feature1: float
    feature2: float


@app.get('/')
def home():
    return {'message': 'Locust demo'}


@app.post('/predict')
def predict(data: InputData):
    time.sleep(2)
    result = data.feature1 + data.feature2
    return {'result': result}