def calculate_discount(price: float, discount: float) -> float:
    if price < 0 or discount < 0 or discount > 100:
        raise ValueError("Invalid price or discount percentage")
    return price - (price * (discount / 100))

def is_password_strong(password: str) -> bool:
    # Strong if password is at least 8 characters long
    return len(password) >= 8
