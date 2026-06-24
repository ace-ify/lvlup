from app import schemas

def calculate_prediction(features: schemas.CarFeatures) -> float:
    """Mock ML prediction logic."""
    base_price = 50000
    age_penalty = (2025 - features.year) * 1000
    mileage_penalty = features.mileage * 0.1
    engine_bonus = features.engine_size * 5000
    
    final_prediction = base_price - age_penalty - mileage_penalty + engine_bonus
    
    if final_prediction < 1000:
        final_prediction = 1000
        
    return final_prediction
