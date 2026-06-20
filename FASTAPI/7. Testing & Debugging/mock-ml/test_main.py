from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)


def test_predict_with_mock():
    with patch('model.model.predict') as mock_predict:
        mock_predict.return_value = [99]
        response = client.post(
            '/predict',
            json={
                'SepalLengthCm': 5.5,
                'SepalWidthCm': 2.1,
                'PetalLengthCm': 4.3,
                'PetalWidthCm': 1.25
            }
        )
        assert response.status_code == 200
        assert response.json() == {'prediction': 99}

# Challenge 5: Write a test for the '/get-weather' endpoint mocking the external HTTP request.
# You need to mock 'httpx.get'.
# Tip: Set mock_get.return_value.json.return_value = {'current': {'temp_c': 25.5}}
# Then verify that the status code is 200 and the response JSON matches {'city': 'Delhi', 'temperature': 25.5}
def test_weather():
    with patch('httpx.get') as mock_get:
        mock_get.return_value.json.return_value = {'current': {'temp_c': 25.5}}
        response = client.get('/get-weather?city=Lucknow')
        assert response.status_code == 200
        assert response.json() == {'city': 'Lucknow', 'temperature': 25.5}