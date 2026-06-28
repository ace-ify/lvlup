import numpy as np
from typing import List

def make_prediction(model, data: dict) -> float:
    features = np.array([
        [
            data['longitude'],
            data['latitude'],
            data['housing_median_age'],
            data['total_rooms'],
            data['total_bedrooms'],
            data['population'],
            data['households'],
            data['median_income']
        ]
    ])
    return model.predict(features)[0]

def make_batchpredictions(model, data: List[dict]) -> np.array:
    X = np.array([
        [
            x['longitude'],
            x['latitude'],
            x['housing_median_age'],
            x['total_rooms'],
            x['total_bedrooms'],
            x['population'],
            x['households'],
            x['median_income']
        ]
        for x in data
    ])
    return model.predict(X)

    