import pytest
from app.math_helper import calculate_discount, is_password_strong

# Write your tests here!
# Challenge 1: Write a test for calculate_discount with normal values (e.g. price 100, discount 10)
# Challenge 2: Write a test for calculate_discount that expects a ValueError for invalid inputs
# Challenge 3: Write tests for is_password_strong with safe, weak, and boundary length passwords
def test_calculate_discount_normal():
    assert calculate_discount(100,10) == 90

def test_calculate_discount_invalid_price():
    with pytest.raises(ValueError):
        calculate_discount(-100,10)

def test_password_strong():
    assert is_password_strong("SecurePa$$w0rd!") is True

def test_password_weak():
    assert is_password_strong("weak") is False
        