from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_eligibility_pass():
    payload = {
        'income': 60000,
        'age': 25,
        'employment_status': 'employed'
    }
    response = client.post('/loan-eligibility', json=payload)
    assert response.status_code == 200
    assert response.json() == {'eligible': True}


def test_eligibility_fail():
    payload = {
        'income': 30000,
        'age': 18,
        'employment_status': 'unemployed'
    }
    response = client.post('/loan-eligibility', json=payload)
    assert response.status_code == 200
    assert response.json() == {'eligible': False}

# Challenge 4: Write an integration test for the '/password-strength' endpoint
# Write a test that sends a strong password and checks if the response code is 200 and 'strong' is True.
# Write another test that sends a weak password and checks if the response code is 200 and 'strong' is False.
def test_password_strong():
    payload = {'password': 'SecurePa$$w0rd!'}
    response = client.post('/password-strength', json=payload)
    assert response.status_code == 200
    assert response.json() == {'strong': True}

def test_password_weak():
    payload = {'password': 'weak'}
    response = client.post('/password-strength', json=payload)
    assert response.status_code == 400
    assert response.json() == {'strong': False}
