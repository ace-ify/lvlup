def is_eligible_for_loan(
        income: float, age: int, employment_status: str
) -> bool:
    return (income >= 50000) and (age >= 21) and (employment_status == 'employed')

def is_password_strong(password: str) -> bool:
    return len(password) >= 8