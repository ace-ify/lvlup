from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String,unique=True,index=True)
    hashed_password=Column(String,nullable=False)
    
class PredictionLog(Base):
    __tablename__="prediction_logs"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String,nullable=True)
    features_hash = Column(String, nullable=False)
    prediction_result = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)