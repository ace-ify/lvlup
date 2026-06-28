from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username:str
    password:str

class UserResponse(BaseModel):
    id:int
    username:str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class CarFeatures(BaseModel):
    year: int
    mileage: float
    engine_size: float


class PredictionResponse(BaseModel):
    prediction: float
    model_version: str